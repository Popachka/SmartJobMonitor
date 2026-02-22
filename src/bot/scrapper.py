import asyncio
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from src.infrastructure.config import config
from src.infrastructure.logger import get_app_logger
from src.services.vacancy_service import VacancyService
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.infrastructure.shemas import MessageInfo
from aiogram import Bot
from src.services.match_service import MatchService
from src.bot.notifier import BotNotifier
from telethon.tl.custom.message import Message
from src.infrastructure.metrics import track
logger = get_app_logger(__name__)


class TelegramScraper:
    def __init__(self, session_factory: async_sessionmaker, bot: Bot):
        self.client = TelegramClient(
            'first_session', config.API_ID, config.API_HASH)
        self.session_factory = session_factory
        self._bot = bot

    @staticmethod
    def _normalize_chat_ref(chat: str | int) -> str | int:
        if isinstance(chat, int):
            return chat
        value = str(chat).strip()
        if value.startswith("https://"):
            value = value[len("https://"):]
        elif value.startswith("http://"):
            value = value[len("http://"):]
        if value.startswith("t.me/"):
            value = value[len("t.me/"):]
        if value.startswith("@") or value.startswith("-100"):
            return value
        if value.lstrip("-").isdigit():
            return value
        return f"@{value}"

    def _normalized_channels(self) -> list[str | int]:
        return [self._normalize_chat_ref(chat) for chat in config.CHANNELS]

    @staticmethod
    def _print_qr_to_terminal(url: str) -> None:
        try:
            import qrcode
        except ImportError:
            logger.warning("Install 'qrcode': pip install qrcode")
            return
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        print("\nScan this QR in Telegram -> Settings -> Devices -> Link Desktop Device:\n")
        qr.print_ascii(invert=True)
        print()

    async def _authorize(self) -> None:
        if not self.client.is_connected():
            await self.client.connect()

        if await self.client.is_user_authorized():
            logger.info("Telethon session already authorized.")
            return

        login_mode = (config.TELETHON_LOGIN_MODE or "qr").lower()
        if login_mode == "phone":
            try:
                await self.client.start(phone=config.TELEGRAM_PHONE)
                return
            except PhoneNumberInvalidError:
                logger.error("Invalid phone format. Use +79123456789")
                raise
            except FloodWaitError as exc:
                logger.error(f"Telegram flood wait: {exc.seconds}s")
                raise

        while not await self.client.is_user_authorized():
            qr_login = await self.client.qr_login()
            logger.info("Open this link in Telegram app to confirm login:")
            logger.info(qr_login.url)
            self._print_qr_to_terminal(qr_login.url)
            try:
                await qr_login.wait(timeout=60)
            except asyncio.TimeoutError:
                logger.warning("QR timed out, generating a new one...")
                await qr_login.recreate()
            except SessionPasswordNeededError:
                if not config.TELEGRAM_2FA_PASSWORD:
                    logger.error("2FA is enabled. Set TELEGRAM_2FA_PASSWORD in .env")
                    raise
                await self.client.sign_in(password=config.TELEGRAM_2FA_PASSWORD)

    async def _message_handler(self, event: events.NewMessage.Event):
        session: AsyncSession
        async with track("telegram.message_handler"):
            try:
                message_info = await self._send_to_mirror(event)
                if not message_info:
                    return

                async with self.session_factory() as session:
                    v_service = VacancyService(session)
                    m_service = MatchService(session)

                    parse_result = await v_service.parse_message(message_info)
                    if not parse_result:
                        return

                    async with session.begin():
                        vacancy_id = await v_service.save_vacancy(message_info, parse_result)

                    vacancy_data, candidates = await m_service.get_potential_candidates(vacancy_id)

                for user_data in candidates:
                    try:
                        async with self.session_factory() as session:
                            service = MatchService(
                                session, notifier=BotNotifier(self._bot))
                            score_result = await service.score_match(vacancy_data, user_data)
                            async with session.begin():
                                await service.save_match(
                                    vacancy=vacancy_data,
                                    user=user_data,
                                    score=score_result.score,
                                )
                            await service.notify_match(
                                vacancy=vacancy_data,
                                user=user_data,
                                score=score_result.score,
                            )
                    except Exception as exc:
                        logger.error(
                            f"Match failed for user {user_data.id}: {exc}")

            except Exception as exc:
                logger.exception(f"Handler failed: {exc}")

    async def _send_to_mirror(self, event: events.NewMessage.Event) -> MessageInfo | None:
        message: Message = event.message
        text = (message.text or "")

        if not text:
            logger.info(
                f"Skipping message with empty text (chat_id={event.chat_id}, message_id={message.id})"
            )
            return None

        try:
            mirror_msg: Message = await self.client.forward_messages(
                config.MIRROR_CHANNEL,
                message,
            )
        except Exception:
            logger.exception(
                "Failed to forward message to mirror",
                extra={
                    "source_chat": event.chat_id,
                    "source_message_id": message.id,
                },
            )
            return None

        return MessageInfo(
            mirror_chat_id=mirror_msg.chat_id,
            mirror_message_id=mirror_msg.id,
            text=text,
        )

    async def start(self):
        channels = self._normalized_channels()
        logger.info(f"Scraper listens channels: {channels}")
        self.client.add_event_handler(
            self._message_handler,
            events.NewMessage(chats=channels)
        )
        await self._authorize()
        logger.info("Scraper started.")
        await self.client.run_until_disconnected()

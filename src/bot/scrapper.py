from telethon import TelegramClient, events
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
        self.client.add_event_handler(
            self._message_handler,
            events.NewMessage(chats=config.CHANNELS)
        )
        await self.client.start()
        logger.info("Scraper started.")
        await self.client.run_until_disconnected()

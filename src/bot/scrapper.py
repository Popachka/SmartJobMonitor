from telethon import TelegramClient, events
from src.infrastructure.config import config
from src.infrastructure.logger import get_app_logger
from src.services.vacancy_service import VacancyService
from sqlalchemy.ext.asyncio import async_sessionmaker
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
        self.vacancy_service = VacancyService(session_factory)
        self.match_service = MatchService(
            session_factory, notifier=BotNotifier(bot))

    async def _message_handler(self, event: events.NewMessage.Event):
        async with track("telegram.message_handler") as tracker:
            try:
                message_info = await self._send_to_mirror(event)
                if message_info is None:
                    return
                vacancy_id = await self.vacancy_service.process_vacancy_message(message_info)
                if vacancy_id is None:
                    return

                await self.match_service.process_vacancy_matches(vacancy_id)

            except Exception as exc:
                tracker.mark_error(exc)
                logger.exception(
                    f"Failed to process Telegram message {exc}",
                )

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

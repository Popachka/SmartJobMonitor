from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from src.infrastructure.db import async_session
from src.infrastructure.logger import get_app_logger
from src.repositories.user_repository import UserRepository

logger = get_app_logger(__name__)


class BotNotifier:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_match(self, user_tg_id: int, mirror_chat_id: int, mirror_message_id: int, score: int) -> None:
        try:
            await self.bot.forward_message(
                chat_id=user_tg_id,
                from_chat_id=mirror_chat_id,
                message_id=mirror_message_id,
            )
            message = (
                f"Оценка вакансии под ваше резюме: {score}/100\n"
            )
            await self.bot.send_message(chat_id=user_tg_id, text=message)
        except (TelegramForbiddenError) as e:
            logger.warning(
                "Failed to send notification - marking user inactive",)
            async with async_session() as session:
                repo = UserRepository(session)
                await repo.set_active_by_tg_id(tg_id=user_tg_id, is_active=False)
        except Exception as e:
            logger.warning(
                "Failed to send notification - possible bot blocked or stopped")

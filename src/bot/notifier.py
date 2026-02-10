from aiogram import Bot
from src.infrastructure.logger import get_app_logger

logger = get_app_logger(__name__)


class BotNotifier:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_match(self, user_tg_id: int, mirror_chat_id: int, mirror_message_id: int, score: int) -> None:
        await self.bot.forward_message(
            chat_id=user_tg_id,
            from_chat_id=mirror_chat_id,
            message_id=mirror_message_id,
        )
        message = (
            f"Оценка соответствия: {score}/100\n"
        )
        try:
            await self.bot.send_message(chat_id=user_tg_id, text=message)
        except Exception as e:
            logger.warning("Failed to send notification — possible bot blocked or stopped", extra={"user_tg_id": user_tg_id})

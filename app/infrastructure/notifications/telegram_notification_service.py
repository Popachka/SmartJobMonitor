from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from app.application.ports.notification_port import INotificationService
from app.core.logger import get_app_logger

logger = get_app_logger(__name__)


class TelegramNotificationService(INotificationService):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def dispatch_vacancy(
        self,
        vacancy_id: UUID,
        mirror_chat_id: int,
        mirror_message_id: int,
        user_ids: list[int],
    ) -> None:
        logger.info(
            "Dispatch vacancy %s (%s:%s) to %s users",
            vacancy_id,
            mirror_chat_id,
            mirror_message_id,
            len(user_ids),
        )
        for user_id in user_ids:
            try:
                await self._bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=mirror_chat_id,
                    message_id=mirror_message_id,
                )
            except TelegramForbiddenError:
                logger.warning(
                    "Failed to forward vacancy %s to user %s: bot forbidden",
                    vacancy_id,
                    user_id,
                )
            except Exception:
                logger.exception(
                    "Failed to forward vacancy %s to user %s",
                    vacancy_id,
                    user_id,
                )

        logger.info("Dispatch finished for vacancy %s", vacancy_id)

from uuid import UUID

from app.application.ports.notification_port import INotificationService
from app.core.logger import get_app_logger

logger = get_app_logger(__name__)


class NoopNotificationService(INotificationService):
    async def dispatch_vacancy(self, vacancy_id: UUID, user_ids: list[int]) -> None:
        logger.info(
            "Noop notification dispatch for vacancy %s to %s users",
            vacancy_id,
            len(user_ids),
        )

# Работа с вакансиями (DB + Logic)
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.vacancy import RawVacancy
from src.core.logger import get_app_logger

logger = get_app_logger(__name__)

class VacancyService:
    def __init__(self, session: AsyncSession):
        self.session = session
    async def create_raw_vacancy(self, text: str, chat_id: int, message_id: int) -> RawVacancy:
        try:
            raw = RawVacancy(
                raw_text=text,
                chat_id=chat_id,
                message_id=message_id,
                status=0
            )
            self.session.add(raw)
            await self.session.commit()
            await self.session.refresh(raw)
            return raw
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка сохранения вакансии в Service: {e}")
            raise
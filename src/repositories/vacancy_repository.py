# Работа с вакансиями (Repository)
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.vacancy import RawVacancy, Vacancy
from src.infrastructure.logger import get_app_logger
from src.schemas.vacancy import VacancyParsedSchema

logger = get_app_logger(__name__)

class VacancyRepository:
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
            logger.error(f"Ошибка сохранения вакансии в Repository: {e}")
            raise

    async def save_parsed_vacancy(self, raw_id: int, vacancy: VacancyParsedSchema):
        try:
            new_vacancy = Vacancy(
                raw_id=raw_id,
                title=vacancy.title,
                tech_stack=vacancy.tech_stack
            )
            self.session.add(new_vacancy)
            await self.session.commit()
            await self.session.refresh(new_vacancy)
            return new_vacancy
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при сохранении обработанной вакансии: {e}")
            raise

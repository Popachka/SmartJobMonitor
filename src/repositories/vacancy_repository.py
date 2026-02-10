# Работа с вакансиями (Repository)
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.logger import get_app_logger
from src.models.vacancy import Vacancy

logger = get_app_logger(__name__)


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        return await self.session.get(Vacancy, vacancy_id)

    async def create_vacancy(
        self,
        text: str,
        main_programming_language: str | None,
        tech_stack: list[str],
        mirror_chat_id: int,
        mirror_message_id: int,
    ) -> Vacancy:
        try:
            vacancy = Vacancy(
                text=text,
                main_programming_language=main_programming_language,
                tech_stack=tech_stack,
                mirror_chat_id=mirror_chat_id,
                mirror_message_id=mirror_message_id,
            )
            self.session.add(vacancy)
            await self.session.commit()
            await self.session.refresh(vacancy)
            return vacancy
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при сохранении вакансии: {e}")
            raise

from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.shemas import VacancyCreateDTO
from src.infrastructure.logger import get_app_logger
from src.models.vacancy import Vacancy

logger = get_app_logger(__name__)


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        return await self.session.get(Vacancy, vacancy_id)

    async def create_vacancy(self, dto: VacancyCreateDTO) -> Vacancy:
        try:
            vacancy = Vacancy(**dto.model_dump())

            self.session.add(vacancy)
            await self.session.commit()
            await self.session.refresh(vacancy)
            return vacancy
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при сохранении вакансии: {e}")
            raise

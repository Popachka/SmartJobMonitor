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

    async def create(self, dto: VacancyCreateDTO) -> Vacancy:
        vacancy = Vacancy(**dto.model_dump())
        self.session.add(vacancy)
        await self.session.flush()
        await self.session.refresh(vacancy)
        return vacancy


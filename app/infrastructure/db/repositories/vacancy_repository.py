from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.repository import IVacancyReader, IVacancyRepository
from app.domain.vacancy.value_objects import ContentHash, VacancyId


class VacancyRepository(IVacancyRepository, IVacancyReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, vacancy_id: VacancyId) -> Vacancy | None:
        raise NotImplementedError

    async def get_by_content_hash(self, content_hash: ContentHash) -> Vacancy | None:
        raise NotImplementedError

    async def exists_by_content_hash(self, content_hash: ContentHash) -> bool:
        raise NotImplementedError

    async def add(self, vacancy: Vacancy) -> None:
        raise NotImplementedError

    async def update(self, vacancy: Vacancy) -> None:
        raise NotImplementedError

    async def upsert(self, vacancy: Vacancy) -> None:
        raise NotImplementedError

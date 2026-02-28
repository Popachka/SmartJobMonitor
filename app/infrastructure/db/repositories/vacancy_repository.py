from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.repository import IVacancyReader, IVacancyRepository
from app.domain.vacancy.value_objects import ContentHash, VacancyId
from app.infrastructure.db.mappers.vacancy import (
    apply_vacancy,
    vacancy_from_model,
    vacancy_to_model,
)
from app.infrastructure.db.models import Vacancy as VacancyModel


class VacancyRepository(IVacancyRepository, IVacancyReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, vacancy_id: VacancyId) -> Vacancy | None:
        result = await self._session.execute(
            select(VacancyModel).where(VacancyModel.id == vacancy_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return vacancy_from_model(model)

    async def get_by_content_hash(self, content_hash: ContentHash) -> Vacancy | None:
        result = await self._session.execute(
            select(VacancyModel).where(VacancyModel.content_hash == content_hash.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return vacancy_from_model(model)

    async def exists_by_content_hash(self, content_hash: ContentHash) -> bool:
        result = await self._session.execute(
            select(VacancyModel.id).where(VacancyModel.content_hash == content_hash.value)
        )
        return result.scalar_one_or_none() is not None

    async def add(self, vacancy: Vacancy) -> None:
        self._session.add(vacancy_to_model(vacancy))

    async def update(self, vacancy: Vacancy) -> None:
        result = await self._session.execute(
            select(VacancyModel).where(VacancyModel.id == vacancy.id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError("Vacancy not found")
        apply_vacancy(model, vacancy)

    async def upsert(self, vacancy: Vacancy) -> None:
        result = await self._session.execute(
            select(VacancyModel).where(VacancyModel.content_hash == vacancy.content_hash.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            self._session.add(vacancy_to_model(vacancy))
            return
        apply_vacancy(model, vacancy)

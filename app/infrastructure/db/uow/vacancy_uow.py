from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.unit_of_work import VacancyUnitOfWork as VacancyUnitOfWorkPort
from app.infrastructure.db.repositories.vacancy_repository import VacancyRepository
from app.infrastructure.db.uow.base import SQLAlchemyUnitOfWork


class VacancyUnitOfWork(SQLAlchemyUnitOfWork, VacancyUnitOfWorkPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)
        self.vacancies: VacancyRepository | None = None

    async def __aenter__(self) -> "VacancyUnitOfWork":
        await super().__aenter__()
        self.vacancies = VacancyRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            self.vacancies = None

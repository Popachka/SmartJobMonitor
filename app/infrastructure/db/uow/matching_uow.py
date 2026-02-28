from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.unit_of_work import MatchingUnitOfWork as MatchingUnitOfWorkPort
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.repositories.vacancy_repository import VacancyRepository
from app.infrastructure.db.uow.base import SQLAlchemyUnitOfWork


class MatchingUnitOfWork(SQLAlchemyUnitOfWork, MatchingUnitOfWorkPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)
        self.users: UserRepository | None = None
        self.vacancies: VacancyRepository | None = None

    async def __aenter__(self) -> "MatchingUnitOfWork":
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.vacancies = VacancyRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            self.users = None
            self.vacancies = None

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.unit_of_work import UserUnitOfWork as UserUnitOfWorkPort
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.uow.base import SQLAlchemyUnitOfWork


class UserUnitOfWork(SQLAlchemyUnitOfWork, UserUnitOfWorkPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)
        self.users: UserRepository | None = None

    async def __aenter__(self) -> "UserUnitOfWork":
        await super().__aenter__()
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            self.users = None

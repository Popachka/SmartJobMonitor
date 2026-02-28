from typing import Protocol

from app.domain.user.repository import IUserRepository
from app.domain.vacancy.repository import IVacancyRepository


class UnitOfWork(Protocol):
    """Protocol for Unit of Work pattern implementation."""

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class VacancyUnitOfWork(UnitOfWork, Protocol):
    vacancies: IVacancyRepository


class UserUnitOfWork(UnitOfWork, Protocol):
    users: IUserRepository

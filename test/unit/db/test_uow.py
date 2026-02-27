import pytest

from app.infrastructure.db.uow.base import SQLAlchemyUnitOfWork
from app.infrastructure.db.uow.vacancy_uow import VacancyUnitOfWork


class FakeSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1

    async def close(self) -> None:
        self.close_calls += 1


class FakeSessionFactory:
    def __init__(self, session: FakeSession) -> None:
        self._session = session
        self.calls = 0

    def __call__(self) -> FakeSession:
        self.calls += 1
        return self._session


@pytest.mark.asyncio
async def test_base_uow_commits_on_success() -> None:
    session = FakeSession()
    uow = SQLAlchemyUnitOfWork(FakeSessionFactory(session))

    async with uow:
        pass

    assert session.commit_calls == 1
    assert session.rollback_calls == 0
    assert session.close_calls == 1


@pytest.mark.asyncio
async def test_base_uow_rolls_back_on_error() -> None:
    session = FakeSession()
    uow = SQLAlchemyUnitOfWork(FakeSessionFactory(session))

    with pytest.raises(RuntimeError):
        async with uow:
            raise RuntimeError("boom")

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    assert session.close_calls == 1


@pytest.mark.asyncio
async def test_vacancy_uow_sets_repo() -> None:
    session = FakeSession()
    uow = VacancyUnitOfWork(FakeSessionFactory(session))

    async with uow:
        assert uow.vacancies is not None

    assert uow.vacancies is None

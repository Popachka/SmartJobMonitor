import os
from typing import AsyncIterator

import psycopg2
import pytest
import pytest_asyncio
from psycopg2 import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import config
from app.infrastructure.db.models import Base

_DEFAULT_TEST_USER = "user"
_DEFAULT_TEST_PASSWORD = "pass"


def _ensure_test_db(db_name: str) -> None:
    if (
        config.POSTGRES_USER == _DEFAULT_TEST_USER
        and config.POSTGRES_PASSWORD == _DEFAULT_TEST_PASSWORD
    ):
        pytest.skip(
            "Postgres credentials are defaults. "
            "Set POSTGRES_USER/POSTGRES_PASSWORD (and host/port) before running integration tests."
        )

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            host=config.POSTGRES_SERVER,
            port=config.POSTGRES_PORT,
        )
    except OperationalError as exc:
        pytest.skip(f"Postgres is unavailable or credentials invalid: {exc}")

    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}"')
    conn.close()


@pytest.fixture(scope="session")
def test_db_name() -> str:
    env_db = os.getenv("POSTGRES_TEST_DB")
    if env_db:
        return env_db
    return f"{config.POSTGRES_DB}_test"


@pytest.fixture(scope="session")
def async_engine(test_db_name: str):
    _ensure_test_db(test_db_name)
    url = str(
        config.ASYNC_SQLALCHEMY_DATABASE_URI
    ).replace(f"/{config.POSTGRES_DB}", f"/{test_db_name}")
    return create_async_engine(url)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db(async_engine) -> AsyncIterator[None]:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


@pytest_asyncio.fixture()
async def session(async_engine) -> AsyncIterator[AsyncSession]:
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as s:
        yield s

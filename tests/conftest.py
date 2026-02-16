import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from src.models.base import Base
import src.models.vacancy
import src.models.user
import src.models.match
from sqlalchemy.pool import NullPool

# Рекомендую вынести тестовый URL в отдельную константу или через env
TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/job_monitor_test"

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    # Создаем движок один раз на всю сессию тестов
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    
    async with engine.begin() as conn:
        # Чистим базу перед началом всех тестов
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture()
async def db_session(db_engine):
    """Фикстура для тестов, требующих чистую БД."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    
    async with session_factory() as session:
        # Очистка перед тестом (защита от мусора предыдущих запусков)
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        await session.commit()
        
        yield session
        await session.rollback()

@pytest_asyncio.fixture()
async def db_sessionmaker(db_engine):
    """Для сервисов, которым нужно самим создавать сессии (как твои Scraper или MatchService)."""
    return async_sessionmaker(db_engine, expire_on_commit=False)
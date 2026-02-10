from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.infrastructure.config import config

engine = create_async_engine(config.ASYNC_SQLALCHEMY_DATABASE_URI, echo = False, future = True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with async_session() as session:
        yield session


async def init_db():
    from src.models.base import Base
    import src.models.vacancy
    import src.models.user
    import src.models.match

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

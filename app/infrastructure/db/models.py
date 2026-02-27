from __future__ import annotations

from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text)

    specializations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    primary_languages: Mapped[list[str]] = mapped_column(JSONB, default=list)
    tech_stack: Mapped[list[str]] = mapped_column(JSONB, default=list)

    min_experience_months: Mapped[int] = mapped_column(Integer, default=0)

    mirror_chat_id: Mapped[int] = mapped_column(BigInteger)
    mirror_message_id: Mapped[int] = mapped_column(BigInteger)

    content_hash: Mapped[str] = mapped_column(String, unique=True, index=True)

    salary_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String, nullable=True)

    work_format: Mapped[str] = mapped_column(String, default="UNDEFINED")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


async def init_db() -> None:
    from app.infrastructure.db.session import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

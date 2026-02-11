from sqlalchemy import BigInteger, String, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)

    text_resume: Mapped[str | None] = mapped_column(Text, nullable=True)

    specializations: Mapped[list[str] | None] = mapped_column(JSONB, default=[])

    primary_languages: Mapped[list[str] | None] = mapped_column(JSONB, default=[])

    experience_months: Mapped[int] = mapped_column(Integer, default=0)

    tech_stack: Mapped[list[str] | None] = mapped_column(JSONB, default=[])

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

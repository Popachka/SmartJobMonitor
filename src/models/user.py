from sqlalchemy import BigInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    text_resume: Mapped[str | None] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    main_programming_language: Mapped[str | None] = mapped_column(String, nullable=True)

from sqlalchemy import BigInteger, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)

    specializations: Mapped[list[str]] = mapped_column(JSONB, default=[])
    primary_languages: Mapped[list[str]] = mapped_column(JSONB, default=[])

    min_experience_months: Mapped[int] = mapped_column(Integer, default=0)

    tech_stack: Mapped[list[str]] = mapped_column(JSONB, default=[])

    mirror_chat_id: Mapped[int] = mapped_column(BigInteger)
    mirror_message_id: Mapped[int] = mapped_column(BigInteger)

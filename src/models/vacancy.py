from sqlalchemy import String, Text, ForeignKey, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.models.base import Base

class RawVacancy(Base):
    __tablename__ = "raw_vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Статус обработки: 0 - новый, 1 - обработан, 2 - ошибка
    status: Mapped[int] = mapped_column(default=0)

    parsed_vacancy: Mapped["Vacancy"] = relationship(back_populates="raw_parent", uselist=False)

class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_id: Mapped[int] = mapped_column(ForeignKey("raw_vacancies.id"))
    
    title: Mapped[str] = mapped_column(String(255))
    
    from sqlalchemy.dialects.postgresql import JSONB
    tech_stack: Mapped[list] = mapped_column(JSONB)

    raw_parent: Mapped["RawVacancy"] = relationship(back_populates="parsed_vacancy")
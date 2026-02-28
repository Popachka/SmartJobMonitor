from pydantic import BaseModel, Field

from app.domain.vacancy.value_objects import (
    LanguageType,
    Salary,
    SpecializationType,
    WorkFormat,
)


class OutResumeParse(BaseModel):
    is_resume: bool = Field(
        ...,
        description=(
            "Признак того, является ли предоставленный документ резюме или профилем кандидата."
        ),
    )
    full_relevant_text_from_resume: str | None = Field(
        default=None,
        description="Полный текст резюме. Если это не резюме, верни None.",
    )
    specializations: list[SpecializationType] = Field(
        default_factory=list,
        description="Список специализаций. Если Fullstack, можно указать [Backend, Frontend].",
    )
    primary_languages: list[LanguageType] = Field(
        default_factory=list,
        description="Основные языки программирования.",
    )
    experience_months: int = Field(
        default=0,
        description="Общий коммерческий опыт в месяцах. Преобразуй года в месяцы.",
    )
    tech_stack: list[str] = Field(
        default_factory=list,
        description=(
            "Список технологий: фреймворки, БД, инструменты (FastAPI, Docker, PostgreSQL)."
        ),
    )
    salary: Salary | None = Field(
        default=None,
        description=(
            "Желаемая зарплата. Если указан диапазон — бери минимум. "
            "Если нету информации о зарплате — null. Валюта может быть null."
        ),
    )
    work_format: WorkFormat = Field(
        default=WorkFormat.UNDEFINED,
        description="Формат работы (REMOTE, HYBRID, ONSITE, UNDEFINED).",
    )

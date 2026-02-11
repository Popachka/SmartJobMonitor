from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from src.infrastructure.llm_provider import get_google_model
from src.infrastructure.shemas import SPECIALIZATIONS, LANGUAGES
from functools import lru_cache


class OutVacancyParse(BaseModel):
    """Схема структурированных данных вакансии."""
    is_vacancy: bool = Field(
        ...,
        description="Признак того, является ли текст описанием вакансии (job description)."
    )
    specializations: List[SPECIALIZATIONS] = Field(
        default_factory=list,
        description="Области разработки. Если ищут фулстека — укажи [Backend, Frontend]."
    )

    primary_languages: List[LANGUAGES] = Field(
        default_factory=list,
        description="Основные языки программирования, требуемые в вакансии."
    )

    min_experience_months: int = Field(
        default=0,
        description="Минимально требуемый опыт в месяцах. Если указано 'от 3 лет' -> 36. Если грейд 'Junior' без лет -> 12."
    )

    tech_stack: List[str] = Field(
        default_factory=list,
        description="Ключевые инструменты и фреймворки (Django, React, Kubernetes)."
    )


@lru_cache(maxsize=1)
def get_vacancy_parse_agent() -> Agent[None, OutVacancyParse]:
    """Инициализирует агента для анализа текста вакансий."""

    system_prompt = (
        "Ты — эксперт по анализу IT-вакансий. Твоя задача: структурировать текст вакансии.\n\n"
        "Правила извлечения:\n"
        "1. 'is_vacancy': установи false, если это любая реклама курсов, резюме или просто флуд. Нас интересуют только IT вакансии, или близкие к IT\n"
        "2. 'specializations': выбери подходящие из списка. Если вакансия широкая (например, системный программист), выбери наиболее близкое.\n"
        "3. 'min_experience_months':\n"
        "   - Если указано 'от X лет', умножай X на 12.\n"
        "   - Если указан диапазон '2-4 года', бери нижнюю границу (24).\n"
        "   - Если годы не указаны, ориентируйся на грейд: Internship=0, Junior=12, Middle=36, Senior=60.\n"
        "4. 'primary_languages': выбирай только из списка разрешенных (Literal). Если языка нет в списке — игнорируй.\n"
        "5. 'tech_stack': извлекай конкретные технологии (FastAPI, PostgreSQL и т.д.)."
    )

    return Agent[None, OutVacancyParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutVacancyParse
    )

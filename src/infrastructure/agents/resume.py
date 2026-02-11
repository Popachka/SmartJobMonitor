from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from src.infrastructure.llm_provider import get_google_model
from src.infrastructure.shemas import SPECIALIZATIONS, LANGUAGES
from functools import lru_cache


class OutResumeParse(BaseModel):
                                                
    is_resume: bool = Field(
        ...,
        description="Признак того, является ли предоставленный документ резюме или профессиональным профилем кандидата."
    )
    full_relevant_text_from_resume: str | None = Field(
        default=None,
        description="Полный текст резюме. Если это не резюме, верни None."
    )
    specializations: List[SPECIALIZATIONS] = Field(
        default_factory=list,
        description="Список специализаций. Если Fullstack, можно указать [Backend, Frontend]"
    )
    primary_languages: List[LANGUAGES] = Field(
        default_factory=list,
        description="Основные языки программирования."
    )

    experience_months: int = Field(
        default=0,
        description="Общий коммерческий опыт в месяцах. Преобразуй года в месяцы (напр. 1.5 года = 18)."
    )

    tech_stack: List[str] = Field(
        default_factory=list,
        description="Список технологий: фреймворки, БД, инструменты (FastAPI, Docker, PostgreSQL)."
    )


@lru_cache(maxsize=1)
def get_resume_parse_agent() -> Agent:
                                                    
    system_prompt = (
        "Ты — эксперт по анализу технических резюме. Твоя задача: перевести неструктурированный текст в признаки.\n\n"
        "ПРАВИЛА ИЗВЛЕЧЕНИЯ:\n"
        "1. 'is_resume': true только для CV и профилей опыта.\n"
        "2. 'specializations': выбери только из списка Literal.\n"
        "3. 'primary_languages': выбери только из списка Literal.\n"
        "4. 'experience_months': РАССЧИТАЙ общий коммерческий опыт.\n"
        "   - Если указано '3 года', пиши 36.\n"
        "   - Если указаны даты (н-р, октябрь 2022 - по н.в.), вычисли количество полных месяцев.\n"
        "   - Игнорируй пет-проекты.\n"
        "5. 'tech_stack': извлеки фреймворки и БД (FastAPI, PostgreSQL). Не дублируй языки.\n"
        "6. 'full_relevant_text_from_resume': сохрани текст без изменений.\n"
    )

    return Agent[None, OutResumeParse](
        get_google_model(),
        system_prompt=system_prompt,
        output_type=OutResumeParse
    )

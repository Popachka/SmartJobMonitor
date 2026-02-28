from functools import lru_cache

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, Model
from pydantic_ai.providers.google import GoogleProvider

from app.application.dto import OutResumeParse, OutVacancyParse
from app.application.ports.llm_port import ILLMExtractor
from app.core.config import config


def get_google_model() -> Model:
    provider = GoogleProvider(api_key=config.GOOGLE_API_KEY)
    return GoogleModel(config.GOOGLE_MODEL, provider=provider)


@lru_cache(maxsize=1)
def get_vacancy_parse_agent() -> Agent[None, OutVacancyParse]:
    system_prompt = (
        "Ты — строгий фильтр IT-вакансий. Ошибка — если принять не‑вакансию.\n\n"
        "СНАЧАЛА реши is_vacancy.\n"
        "is_vacancy = false, если:\n"
        "- текст похож на списки технологий/стек без описания роли/задач/условий;\n"
        "- нет явной роли (позиции) или задач;\n"
        "- это реклама, курс, резюме, подборка вакансий, просто новости;\n"
        "- нет требований/обязанностей/условий.\n\n"
        "is_vacancy = true только если есть:\n"
        "- явная роль (например, 'Frontend developer');\n"
        "- задачи ИЛИ требования ИЛИ условия работы.\n\n"
        "Если сомневаешься — ставь false.\n"
        "Только IT-вакансии.\n\n"
        "Дальше извлекай поля...\n"
        "2. 'specializations': выбери подходящие из списка. Если вакансия широкая (например, системный программист), выбери наиболее близкое.\n"
        "3. 'min_experience_months':\n"
        "   - Если указано 'от X лет', умножай X на 12.\n"
        "   - Если указан диапазон '2-4 года', бери нижнюю границу (24).\n"
        "   - Если годы не указаны, ориентируйся на грейд: Internship=0, Junior=12, Middle=36, Senior=60.\n"
        "4. 'primary_languages': выбирай только из списка разрешенных (Literal). Если языка нет в списке — игнорируй.\n"
        "5. 'tech_stack': извлекай конкретные технологии (FastAPI, PostgreSQL и т.д.).\n"
        "6. 'salary': если указан диапазон (например, 15000-20000) — бери минимальную сумму. "
        "Если зарплата не указана — верни null. Валюту бери из описания, если не указана — null.\n"
        "7. 'work_format': выбирай одно из [REMOTE, HYBRID, ONSITE, UNDEFINED]. Если нет явного указания — UNDEFINED."
    )

    return Agent[None, OutVacancyParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutVacancyParse,
    )


@lru_cache(maxsize=1)
def get_resume_parse_agent() -> Agent[None, OutResumeParse]:
    system_prompt = (
        "Ты — эксперт по анализу технических резюме. Твоя задача: перевести "
        "неструктурированный текст в признаки.\n\n"
        "ПРАВИЛА ИЗВЛЕЧЕНИЯ:\n"
        "1. 'is_resume': true только для CV и профилей опыта.\n"
        "2. 'specializations': выбери только из списка Literal.\n"
        "3. 'primary_languages': выбери только из списка Literal.\n"
        "4. 'experience_months': РАССЧИТАЙ общий коммерческий опыт.\n"
        "   - Если указано '3 года', пиши 36.\n"
        "   - Если указаны даты (н-р, октябрь 2022 - по н.в.), вычисли количество "
        "полных месяцев.\n"
        "   - Игнорируй пет-проекты.\n"
        "5. 'tech_stack': извлеки фреймворки и БД (FastAPI, PostgreSQL). "
        "Не дублируй языки.\n"
        "6. 'salary': желаемая зарплата. Если указан диапазон — бери минимум. "
        "Если зарплата не указана — верни null. Валюта может быть null.\n"
        "7. 'work_format': выбирай одно из [REMOTE, HYBRID, ONSITE, UNDEFINED]. "
        "Если нет явного указания — UNDEFINED.\n"
        "8. 'full_relevant_text_from_resume': сохрани текст без изменений.\n"
    )

    return Agent[None, OutResumeParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutResumeParse,
    )


class GoogleLLMExtractor(ILLMExtractor):
    def __init__(self) -> None:
        self._agent = get_vacancy_parse_agent()

    async def parse_vacancy(self, text: str) -> OutVacancyParse:
        result = await self._agent.run(user_prompt=f"Текст вакансии:\n{text}")
        return result.output

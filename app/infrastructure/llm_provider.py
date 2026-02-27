from functools import lru_cache

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, Model
from pydantic_ai.providers.google import GoogleProvider

from app.application.dto.vacancy_dto import OutVacancyParse
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


class GoogleLLMExtractor(ILLMExtractor):
    def __init__(self) -> None:
        self._agent = get_vacancy_parse_agent()

    async def parse_vacancy(self, text: str) -> OutVacancyParse:
        result = await self._agent.run(user_prompt=f"Текст вакансии:\n{text}")
        return result.output

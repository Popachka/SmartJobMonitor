from functools import lru_cache

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, Model
from pydantic_ai.providers.google import GoogleProvider

from app.application.dto import OutResumeParse, OutResumeSalaryParse, OutVacancyParse
from app.core.config import config
from app.domain.shared.value_objects import SkillType


def get_google_model() -> Model:
    provider = GoogleProvider(api_key=config.GOOGLE_API_KEY)
    return GoogleModel(config.GOOGLE_MODEL, provider=provider)


@lru_cache(maxsize=1)
def get_vacancy_parse_agent() -> Agent[None, OutVacancyParse]:
    allowed_skills = ", ".join(skill.value for skill in SkillType)
    system_prompt = (
        "Ты — строгий парсер IT-вакансий.\n"
        "Сначала реши, является ли текст вакансией.\n"
        "Возвращай is_vacancy=false, если в тексте нет явной роли и требований, задач или условий.\n\n"
        "Если это вакансия, извлеки:\n"
        "1. specializations только из фиксированного списка.\n"
        f"2. skills только из SkillType: {allowed_skills}.\n"
        "   - Извлекай только явные упоминания.\n"
        "   - React и Vue сохраняй как отдельные skills.\n"
        "   - Не придумывай skills вне списка.\n"
        "3. salary: если указан диапазон, бери минимум, иначе null.\n"
        "4. work_format: REMOTE, HYBRID, ONSITE или UNDEFINED.\n"
    )

    return Agent[None, OutVacancyParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutVacancyParse,
        name="vacancy_parser_agent",
        metadata={"agent_type": "vacancy_parser"},
    )


@lru_cache(maxsize=1)
def get_resume_parse_agent() -> Agent[None, OutResumeParse]:
    allowed_skills = ", ".join(skill.value for skill in SkillType)
    system_prompt = (
        "Ты — эксперт по разбору технических резюме.\n"
        "Преобразуй резюме в структурированные поля.\n\n"
        "Правила:\n"
        "1. is_resume=true только для резюме и профилей кандидата.\n"
        "2. specializations выбирай только из фиксированного списка.\n"
        f"3. skills выбирай только из SkillType: {allowed_skills}.\n"
        "   - Извлекай только явные упоминания.\n"
        "   - React и Vue сохраняй как отдельные skills.\n"
        "   - Не придумывай skills вне списка.\n"
        "4. salary — желаемая зарплата; если указан диапазон, бери минимум.\n"
        "5. work_format — одно из REMOTE, HYBRID, ONSITE, UNDEFINED.\n"
        "6. full_relevant_text_from_resume сохраняй без искажений.\n"
    )

    return Agent[None, OutResumeParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutResumeParse,
        model_settings={"temperature": 0.0},
        name="resume_parser_agent",
        metadata={"agent_type": "resume_parser"},
    )


@lru_cache(maxsize=1)
def get_resume_salary_agent() -> Agent[None, OutResumeSalaryParse]:
    system_prompt = (
        "Извлеки из резюме только информацию о зарплате.\n"
        "Верни amount, currency и короткий evidence-фрагмент.\n"
        "Если указан диапазон, бери минимум. Если зарплата не указана, верни null.\n"
        "Ничего не придумывай."
    )

    return Agent[None, OutResumeSalaryParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutResumeSalaryParse,
        model_settings={"temperature": 0.0},
        name="resume_salary_agent",
        metadata={"agent_type": "resume_salary"},
    )

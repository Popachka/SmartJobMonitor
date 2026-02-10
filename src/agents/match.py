from pydantic import BaseModel, Field
from pydantic_ai import Agent

from src.infrastructure.llm_provider import get_google_model


class OutMatchParse(BaseModel):
    score: int = Field(ge=0, le=100, description="Оценка соответствия кандидата вакансии от 0 до 100.")


def get_match_agent() -> Agent[None, OutMatchParse]:
    system_prompt = (
        "Вы эксперт по подбору персонала. Получив вакансию и резюме кандидата, "
        "оцените, насколько кандидат подходит под вакансию. "
        "Верните оценку от 0 до 100 и короткое объяснение. "
    )

    return Agent[None, OutMatchParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutMatchParse,
    )

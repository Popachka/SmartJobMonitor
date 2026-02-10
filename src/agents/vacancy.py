from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from src.infrastructure.llm_provider import get_google_model

class OutVacancyParse(BaseModel):
    """Схема структурированных данных вакансии."""
    is_vacancy: bool = Field(
        ..., 
        description="Признак того, является ли текст описанием вакансии (job description)."
    )
    main_programming_language: Optional[str] = Field(
        default=None,
        description="Основной язык программирования, требуемый в вакансии (например, Python, Java, Go). Если не определен — None."
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Список ключевых технологий, фреймворков и инструментов (например, Django, Docker, PostgreSQL)."
    )

def get_vacancy_parse_agent() -> Agent[None, OutVacancyParse]:
    """Инициализирует агента для анализа текста вакансий."""
    
    system_prompt = (
        "Ты — эксперт по анализу IT-вакансий. Твоя задача: определить, является ли предоставленный текст описанием вакансии, "
        "и извлечь ключевую техническую информацию."
        "\n\nПравила анализа:"
        "\n1. 'is_vacancy': установи true, если текст содержит описание позиции, требований или обязанностей. "
        "Если это личное сообщение, реклама курсов, резюме или просто текст — установи false."
        "\n2. Если 'is_vacancy' == false, для остальных полей верни значения по умолчанию (None/[])."
        "\n3. 'main_programming_language': выдели главный язык разработки. Если в вакансии много языков, выбери основной. "
        "Если язык не указан (например, для системного администратора) — None."
        "\n4. 'tech_stack': собери все важные технологии. Будь точен, не выдумывай то, чего нет в тексте."
    )
    
    return Agent[None, OutVacancyParse](
        model=get_google_model(),
        system_prompt=system_prompt,
        output_type=OutVacancyParse  
    )
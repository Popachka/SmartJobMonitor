from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from src.infrastructure.llm_provider import get_google_model

class OutResumeParse(BaseModel):
    """Схема структурированных данных резюме."""
    is_resume: bool = Field(
        ..., 
        description="Признак того, является ли предоставленный документ резюме или профессиональным профилем кандидата."
    )
    full_relevant_text_from_resume: Optional[str] = Field(
        default=None,
        description="Полный текст резюме. Если это не резюме, верни None."
    )
    main_programming_language: Optional[str] = Field(
        default=None,
        description="Основной язык программирования. Если это не резюме или язык не определен, верни None."
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Список технологий. Если это не резюме или технологий не найдено, верни []."
    )

def get_resume_parse_agent() -> Agent:
    """Инициализирует агента для парсинга резюме."""
    
    system_prompt = (
        "Ты — технический OCR-парзер. Твоя задача: определить, является ли документ резюме, и если да, извлечь данные. "
        "Используй язык оригинала документа."
        "\n\nПравила заполнения:"
        "\n1. 'is_resume': установи true, если это резюме, CV, профиль в LinkedIn или описание опыта работы. "
        "Если это счет, случайное фото, книга или любой другой документ — установи false."
        "\n2. Если 'is_resume' == false, то для всех остальных полей возвращай значения по умолчанию (None или [])."
        "\n3. 'full_relevant_text_from_resume': проводи OCR максимально точно, сохраняя структуру."
        "\n4. 'main_programming_language': укажи основной стек. Если его нет — строго None."
        "\n5. 'tech_stack': извлекай только явно упомянутые технологии."
        "\n6. Запрещено галлюцинировать и выдумывать данные."
    )
    
    return Agent[None, OutResumeParse](
        get_google_model(),
        system_prompt=system_prompt,
        output_type=OutResumeParse
    )
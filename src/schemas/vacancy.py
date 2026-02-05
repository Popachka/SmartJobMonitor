# Схема распарсенной вакансии
from pydantic import BaseModel, Field
from typing import List, Optional

class VacancyParsedSchema(BaseModel):
    title: str = Field(description="Название должности (например, Python Developer)")
    tech_stack: List[str] = Field(description="Список технологий (например, ['FastAPI', 'PostgreSQL'])")
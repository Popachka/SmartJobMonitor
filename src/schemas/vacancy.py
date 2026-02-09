# Схема распарсенной вакансии
from pydantic import BaseModel, Field

class VacancyParsedSchema(BaseModel):
    title: str = Field(description="Название должности (например, Python Developer)")
    tech_stack: list[str] = Field(description="Список технологий (например, ['FastAPI', 'PostgreSQL'])")
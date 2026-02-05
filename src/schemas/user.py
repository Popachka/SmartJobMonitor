# Схема профиля пользователя
from pydantic import BaseModel, Field
from typing import List, Optional

class UserCreate(BaseModel):
    tg_id: int
    username: Optional[str] = None

class ResumeParsedSchema(BaseModel):
    """То, что вернет LLM после анализа резюме"""
    tech_stack: List[str] = Field(description="Извлеченный список технологий")
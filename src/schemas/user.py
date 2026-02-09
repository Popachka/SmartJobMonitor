# Схема профиля пользователя
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    tg_id: int
    username: Optional[str] = None

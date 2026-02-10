from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict


@dataclass(frozen=True, slots=True)
class MatchRequest:
    vacancy_text: str
    resume_text: str
    vacancy_lang: str | None
    user_lang: str | None


class UserCreate(BaseModel):
    tg_id: int
    username: str | None = None


@dataclass(frozen=True, slots=True)
class MessageInfo:
    mirror_chat_id: int
    mirror_message_id: int
    text: str


class VacancyData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    main_programming_language: str | None
    mirror_chat_id: int
    mirror_message_id: int

class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    text_resume: str | None
    main_programming_language: str | None

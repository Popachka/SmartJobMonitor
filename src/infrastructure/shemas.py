from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Literal


@dataclass(frozen=True, slots=True)
class MatchRequest:
    vacancy_text: str
    resume_text: str
    vacancy_specs: list[str]
    user_specs: list[str]
    vacancy_langs: list[str]
    user_langs: list[str]
    experience_gap: int


class UserCreate(BaseModel):
    tg_id: int
    username: str | None = None


@dataclass(frozen=True, slots=True)
class MessageInfo:
    mirror_chat_id: int
    mirror_message_id: int
    text: str

@dataclass(frozen=True)
class CandidateCriteria:
    min_experience_months: int
    match_specializations: list[str]
    match_languages: list[str]
    match_mode: Literal["or", "and"] 

class VacancyData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    specializations: list[str]
    primary_languages: list[str]
    min_experience_months: int
    tech_stack: list[str]
    mirror_chat_id: int
    mirror_message_id: int

    @field_validator("specializations", "primary_languages", "tech_stack", mode="before")
    @classmethod
    def _coerce_lists(cls, value):
        return value or []


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    text_resume: str | None
    specializations: list[str]
    primary_languages: list[str]
    experience_months: int
    tech_stack: list[str]

    @field_validator("specializations", "primary_languages", "tech_stack", mode="before")
    @classmethod
    def _coerce_lists(cls, value):
        return value or []


class VacancyCreateDTO(BaseModel):
    text: str
    specializations: list[str]
    primary_languages: list[str]
    min_experience_months: int
    tech_stack: list[str]
    mirror_chat_id: int
    mirror_message_id: int


class UserResumeUpdateDTO(BaseModel):
    specializations: list[str]
    primary_languages: list[str]
    experience_months: int
    tech_stack: list[str]
    text_resume: str | None


SPECIALIZATIONS = Literal[
    "Backend", "Frontend", "Fullstack", "Mobile",
    "DevOps", "Data Science", "QA", "Management"
]

LANGUAGES = Literal[
    "Python", "JavaScript", "TypeScript", "Go",
    "Java", "Kotlin", "Swift", "PHP", "C++", "C#", "Rust", "Ruby"
]

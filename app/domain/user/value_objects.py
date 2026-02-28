from dataclasses import dataclass
from enum import StrEnum

from app.domain.vacancy.value_objects import (
    WorkFormat,
    CurrencyType,
    SpecializationType,
    LanguageType,
    Specializations,
    PrimaryLanguages,
    TechStack,
    Salary,
)


@dataclass(frozen=True, slots=True)
class UserId:
    value: int


class FilterMode(StrEnum):
    STRICT = "STRICT"
    SOFT = "SOFT"


__all__ = [
    "UserId",
    "FilterMode",
    "WorkFormat",
    "CurrencyType",
    "SpecializationType",
    "LanguageType",
    "Specializations",
    "PrimaryLanguages",
    "TechStack",
    "Salary",
]

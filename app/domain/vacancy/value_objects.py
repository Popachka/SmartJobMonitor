from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from uuid import UUID


class WorkFormat(Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    UNDEFINED = "UNDEFINED"


class CurrencyType(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class SpecializationType(StrEnum):
    BACKEND = "Backend"
    FRONTEND = "Frontend"
    FULLSTACK = "Fullstack"
    MOBILE = "Mobile"
    DEVOPS = "DevOps"
    DATA_SCIENCE = "Data Science"
    QA = "QA"
    MANAGEMENT = "Management"


class LanguageType(StrEnum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    GO = "Go"
    JAVA = "Java"
    KOTLIN = "Kotlin"
    SWIFT = "Swift"
    PHP = "PHP"
    CPP = "C++"
    CSHARP = "C#"
    RUST = "Rust"
    RUBY = "Ruby"


@dataclass(frozen=True, slots=True)
class VacancyId:
    value: UUID


@dataclass(frozen=True, slots=True)
class ContentHash:
    value: str


@dataclass(frozen=True, slots=True)
class Specializations:
    items: frozenset[SpecializationType]

    @classmethod
    def from_strs(cls, names: list[str]) -> "Specializations":
        valid_items = []
        for name in names:
            try:
                valid_items.append(SpecializationType(name.strip()))
            except ValueError:
                continue

        return cls(items=frozenset(valid_items))


@dataclass(frozen=True, slots=True)
class PrimaryLanguages:
    items: frozenset[LanguageType]

    @classmethod
    def from_strs(cls, names: list[str]) -> "PrimaryLanguages":
        valid_items = []
        for name in names:
            try:
                valid_items.append(LanguageType(name.strip()))
            except ValueError:
                continue

        return cls(items=frozenset(valid_items))


@dataclass(frozen=True, slots=True)
class TechStack:
    items: frozenset[str]

    @classmethod
    def create(cls, raw_items: list[str] | frozenset[str]) -> "TechStack":
        normalized = frozenset(
            i.strip().capitalize() for i in raw_items if i and i.strip()
        )
        return cls(items=normalized)


@dataclass(frozen=True, slots=True)
class Salary:
    min_amount: int | None
    currency: CurrencyType

    @classmethod
    def create(cls, amount: int | None = None, currency: str = "RUB") -> "Salary":
        if amount is not None and amount < 0:
            raise ValueError("Salary cannot be negative")

        return cls(
            min_amount=amount,
            currency=CurrencyType(currency.upper().strip())
        )

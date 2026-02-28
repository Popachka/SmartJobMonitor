from dataclasses import dataclass
from enum import Enum, StrEnum


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
    def create(cls, raw_items: list[str] | frozenset[str] | None) -> "TechStack":
        normalized = frozenset(
            item.strip().capitalize() for item in (raw_items or []) if item and item.strip()
        )
        return cls(items=normalized)


@dataclass(frozen=True, slots=True)
class Salary:
    amount: int | None
    currency: CurrencyType | None

    @classmethod
    def create(cls, amount: int | None = None, currency: str | None = None) -> "Salary":
        if amount is not None and amount < 0:
            raise ValueError("Salary cannot be negative")

        if currency is None or not currency.strip():
            return cls(amount=amount, currency=None)

        return cls(
            amount=amount,
            currency=CurrencyType(currency.upper().strip()),
        )


__all__ = [
    "WorkFormat",
    "CurrencyType",
    "SpecializationType",
    "LanguageType",
    "Specializations",
    "PrimaryLanguages",
    "TechStack",
    "Salary",
]

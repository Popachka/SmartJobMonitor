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


class SkillType(StrEnum):
    PYTHON = "Python"
    REACT = "React"
    VUE = "Vue"


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
class Skills:
    items: frozenset[SkillType]

    @classmethod
    def from_strs(cls, names: list[str]) -> "Skills":
        valid_items: list[SkillType] = []
        for name in names:
            cleaned = name.strip()
            if not cleaned:
                continue
            try:
                valid_items.append(SkillType(cleaned))
            except ValueError:
                continue

        return cls(items=frozenset(valid_items))


@dataclass(frozen=True, slots=True)
class Salary:
    amount: int | None
    currency: CurrencyType | None

    @classmethod
    def create(cls, amount: int | None = None, currency: str | None = None) -> "Salary":
        if amount is not None and amount < 0:
            raise ValueError("Salary cannot be negative")

        if amount is None:
            return cls(amount=None, currency=None)

        if currency is None or not currency.strip():
            return cls(amount=amount, currency=CurrencyType.RUB)

        normalized_currency = currency.upper().strip()
        if normalized_currency != CurrencyType.RUB.value:
            return cls(amount=None, currency=None)

        return cls(
            amount=amount,
            currency=CurrencyType.RUB,
        )


__all__ = [
    "WorkFormat",
    "CurrencyType",
    "SpecializationType",
    "SkillType",
    "Specializations",
    "Skills",
    "Salary",
]

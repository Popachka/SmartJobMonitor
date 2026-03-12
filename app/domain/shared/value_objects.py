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
    DATA_SCIENCE_ML = "Data Science / ML"
    MOBILE = "Mobile"
    GAMEDEV = "GameDev"
    QA = "QA"
    INFRASTRUCTURE_DEVOPS = "Infrastructure & DevOps"
    ANALYTICS = "Analytics"


class SkillType(StrEnum):
    # Backend
    PYTHON = "Python"
    JAVA_SCALA = "Java/Scala"
    C_SHARP = "C#"
    C_PLUSPLUS = "C++"
    GO = "Go"
    C = "C"
    RUBY = "Ruby"
    PHP = "PHP"
    NODE_JS = "Node.js"
    TYPESCRIPT = "TypeScript"
    KOTLIN = "Kotlin"

    # Frontend
    REACT = "React"
    VUE = "Vue"
    ANGULAR = "Angular"

    # Data Science / ML
    MACHINE_LEARNING = "Machine Learning"
    NLP = "NLP"
    COMPUTER_VISION = "Computer Vision"
    RECOMMENDER_SYSTEMS = "Recommender Systems"

    # Mobile
    IOS = "iOS"
    ANDROID = "Android"
    FLUTTER = "Flutter"
    REACT_NATIVE = "React Native"

    # GameDev
    UNITY = "Unity"
    UNREAL_ENGINE = "Unreal Engine"
    GAMEPLAY_PROGRAMMING = "Gameplay Programming"
    GRAPHICS = "Graphics"

    # QA
    MANUAL_QA = "Manual QA"
    QA_AUTOMATION = "QA Automation"
    PERFORMANCE_TESTING = "Performance Testing"

    # Infrastructure & DevOps
    DEVOPS = "DevOps"
    SRE = "SRE"
    DBA = "DBA"
    SYSTEM_ADMINISTRATION = "System Administration"

    # Analytics
    SQL = "SQL"
    DATA_ANALYSIS = "Data Analysis"


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

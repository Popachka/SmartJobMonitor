from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VacancyId:
    value: UUID


@dataclass(frozen=True, slots=True)
class ContentHash:
    value: str

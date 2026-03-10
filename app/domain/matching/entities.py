from dataclasses import dataclass
from enum import StrEnum


class MatchRejectionReason(StrEnum):
    SALARY = "salary"
    FORMAT = "format"


@dataclass(frozen=True, slots=True)
class MatchDecision:
    accepted: bool
    reason: MatchRejectionReason | None = None

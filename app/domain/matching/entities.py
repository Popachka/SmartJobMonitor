from dataclasses import dataclass
from enum import StrEnum


class MatchRejectionReason(StrEnum):
    EXP = "exp"
    SALARY = "salary"
    STACK = "stack"


@dataclass(frozen=True, slots=True)
class MatchDecision:
    accepted: bool
    reason: MatchRejectionReason | None = None

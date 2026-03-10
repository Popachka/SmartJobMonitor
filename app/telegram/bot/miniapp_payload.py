import json
from dataclasses import dataclass
from enum import StrEnum

from app.domain.shared.value_objects import SkillType, SpecializationType


class WorkFormatChoice(StrEnum):
    ANY = "ANY"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class SalaryModeChoice(StrEnum):
    ANY = "ANY"
    FROM = "FROM"


@dataclass(frozen=True, slots=True)
class MiniAppPayload:
    specializations: frozenset[SpecializationType]
    skills: frozenset[SkillType]
    work_format_choice: WorkFormatChoice
    salary_mode: SalaryModeChoice
    salary_amount_rub: int | None


def parse_miniapp_payload(raw_payload: str) -> MiniAppPayload:
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid mini-app payload") from exc

    if not isinstance(payload, dict):
        raise ValueError("Invalid mini-app payload")

    return MiniAppPayload(
        specializations=_parse_specializations(payload.get("specializations")),
        skills=_parse_skills(payload.get("skills")),
        work_format_choice=_parse_work_format_choice(payload.get("work_format_choice")),
        salary_mode=_parse_salary_mode(payload.get("salary_mode")),
        salary_amount_rub=_parse_salary_amount(payload.get("salary_amount_rub")),
    )


def _parse_specializations(raw_value: object) -> frozenset[SpecializationType]:
    return frozenset(_parse_enum_list(raw_value, SpecializationType))


def _parse_skills(raw_value: object) -> frozenset[SkillType]:
    return frozenset(_parse_enum_list(raw_value, SkillType))


def _parse_enum_list[EnumChoice: StrEnum](
    raw_value: object, enum_type: type[EnumChoice]
) -> list[EnumChoice]:
    if raw_value is None:
        return []
    if not isinstance(raw_value, list):
        raise ValueError("Invalid mini-app payload")

    items: list[EnumChoice] = []
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError("Invalid mini-app payload")
        try:
            items.append(enum_type(item.strip()))
        except ValueError:
            raise ValueError("Invalid mini-app payload") from None
    return items


def _parse_work_format_choice(raw_value: object) -> WorkFormatChoice:
    if raw_value is None:
        return WorkFormatChoice.ANY
    if not isinstance(raw_value, str):
        raise ValueError("Invalid mini-app payload")
    try:
        return WorkFormatChoice(raw_value.strip())
    except ValueError as exc:
        raise ValueError("Invalid mini-app payload") from exc


def _parse_salary_mode(raw_value: object) -> SalaryModeChoice:
    if raw_value is None:
        return SalaryModeChoice.ANY
    if not isinstance(raw_value, str):
        raise ValueError("Invalid mini-app payload")
    try:
        return SalaryModeChoice(raw_value.strip())
    except ValueError as exc:
        raise ValueError("Invalid mini-app payload") from exc


def _parse_salary_amount(raw_value: object) -> int | None:
    if raw_value in (None, ""):
        return None
    if isinstance(raw_value, int):
        return raw_value if raw_value >= 0 else None
    if isinstance(raw_value, str) and raw_value.strip().isdigit():
        return int(raw_value.strip())
    raise ValueError("Invalid mini-app payload")

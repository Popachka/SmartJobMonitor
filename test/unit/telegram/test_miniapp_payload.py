import pytest

from app.domain.shared import SkillType, SpecializationType
from app.telegram.bot.miniapp_payload import parse_miniapp_payload


def test_parse_miniapp_payload_accepts_skills_only() -> None:
    payload = parse_miniapp_payload(
        """
        {
          "specializations": ["Backend"],
          "skills": ["Python", "React"],
          "work_format_choice": "REMOTE",
          "salary_mode": "FROM",
          "salary_amount_rub": 200000
        }
        """
    )

    assert payload.specializations == frozenset({SpecializationType.BACKEND})
    assert payload.skills == frozenset({SkillType.PYTHON, SkillType.REACT})
    assert payload.salary_amount_rub == 200000


def test_parse_miniapp_payload_rejects_invalid_skill() -> None:
    with pytest.raises(ValueError, match="Invalid mini-app payload"):
        parse_miniapp_payload('{"specializations":["Backend"],"skills":["FastAPI"]}')

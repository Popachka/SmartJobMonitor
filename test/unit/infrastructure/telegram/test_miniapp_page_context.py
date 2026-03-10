from app.application.dto.miniapp import WorkFormatChoice
from app.domain.shared import SkillType, SpecializationType, WorkFormat
from app.telegram.miniapp.page_context import (
    build_skill_options,
    build_specialization_options,
    build_work_format_options,
)


def test_build_specialization_options_follows_domain_order() -> None:
    assert build_specialization_options() == [item.value for item in SpecializationType]


def test_build_skill_options_follows_domain_order() -> None:
    assert build_skill_options() == [item.value for item in SkillType]


def test_build_work_format_options_uses_domain_values_without_undefined() -> None:
    options = build_work_format_options()

    assert [(item.value, item.label) for item in options] == [
        (WorkFormatChoice.ANY.value, WorkFormatChoice.ANY.value),
        *[(item.value, item.value) for item in WorkFormat if item is not WorkFormat.UNDEFINED],
    ]

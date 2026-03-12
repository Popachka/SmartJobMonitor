from dataclasses import dataclass

from fastapi import Request

from app.application.dto.miniapp import ChoiceOptionDto, WorkFormatChoice
from app.domain.shared.value_objects import SkillType, SpecializationType, WorkFormat


@dataclass(frozen=True, slots=True)
class SkillOptionView:
    value: str
    label: str
    section: SpecializationType


@dataclass(frozen=True, slots=True)
class SkillSectionView:
    title: str
    options: tuple[SkillOptionView, ...]


_SKILL_SECTION_ORDER = (
    SpecializationType.BACKEND,
    SpecializationType.FRONTEND,
    SpecializationType.DATA_SCIENCE_ML,
    SpecializationType.MOBILE,
    SpecializationType.GAMEDEV,
    SpecializationType.QA,
    SpecializationType.INFRASTRUCTURE_DEVOPS,
    SpecializationType.ANALYTICS,
)
_SKILL_OPTION_VIEWS: tuple[SkillOptionView, ...] = (
    SkillOptionView(
        value=SkillType.PYTHON.value,
        label=SkillType.PYTHON.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.JAVA_SCALA.value,
        label=SkillType.JAVA_SCALA.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.C_SHARP.value,
        label=SkillType.C_SHARP.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.C_PLUSPLUS.value,
        label=SkillType.C_PLUSPLUS.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.GO.value,
        label=SkillType.GO.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.C.value,
        label=SkillType.C.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.RUBY.value,
        label=SkillType.RUBY.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.PHP.value,
        label=SkillType.PHP.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.NODE_JS.value,
        label=SkillType.NODE_JS.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.TYPESCRIPT.value,
        label=SkillType.TYPESCRIPT.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.KOTLIN.value,
        label=SkillType.KOTLIN.value,
        section=SpecializationType.BACKEND,
    ),
    SkillOptionView(
        value=SkillType.REACT.value,
        label=SkillType.REACT.value,
        section=SpecializationType.FRONTEND,
    ),
    SkillOptionView(
        value=SkillType.VUE.value,
        label=SkillType.VUE.value,
        section=SpecializationType.FRONTEND,
    ),
    SkillOptionView(
        value=SkillType.ANGULAR.value,
        label=SkillType.ANGULAR.value,
        section=SpecializationType.FRONTEND,
    ),
    SkillOptionView(
        value=SkillType.MACHINE_LEARNING.value,
        label=SkillType.MACHINE_LEARNING.value,
        section=SpecializationType.DATA_SCIENCE_ML,
    ),
    SkillOptionView(
        value=SkillType.NLP.value,
        label=SkillType.NLP.value,
        section=SpecializationType.DATA_SCIENCE_ML,
    ),
    SkillOptionView(
        value=SkillType.COMPUTER_VISION.value,
        label=SkillType.COMPUTER_VISION.value,
        section=SpecializationType.DATA_SCIENCE_ML,
    ),
    SkillOptionView(
        value=SkillType.RECOMMENDER_SYSTEMS.value,
        label=SkillType.RECOMMENDER_SYSTEMS.value,
        section=SpecializationType.DATA_SCIENCE_ML,
    ),
    SkillOptionView(
        value=SkillType.IOS.value,
        label=SkillType.IOS.value,
        section=SpecializationType.MOBILE,
    ),
    SkillOptionView(
        value=SkillType.ANDROID.value,
        label=SkillType.ANDROID.value,
        section=SpecializationType.MOBILE,
    ),
    SkillOptionView(
        value=SkillType.FLUTTER.value,
        label=SkillType.FLUTTER.value,
        section=SpecializationType.MOBILE,
    ),
    SkillOptionView(
        value=SkillType.REACT_NATIVE.value,
        label=SkillType.REACT_NATIVE.value,
        section=SpecializationType.MOBILE,
    ),
    SkillOptionView(
        value=SkillType.UNITY.value,
        label=SkillType.UNITY.value,
        section=SpecializationType.GAMEDEV,
    ),
    SkillOptionView(
        value=SkillType.UNREAL_ENGINE.value,
        label=SkillType.UNREAL_ENGINE.value,
        section=SpecializationType.GAMEDEV,
    ),
    SkillOptionView(
        value=SkillType.GAMEPLAY_PROGRAMMING.value,
        label=SkillType.GAMEPLAY_PROGRAMMING.value,
        section=SpecializationType.GAMEDEV,
    ),
    SkillOptionView(
        value=SkillType.GRAPHICS.value,
        label=SkillType.GRAPHICS.value,
        section=SpecializationType.GAMEDEV,
    ),
    SkillOptionView(
        value=SkillType.MANUAL_QA.value,
        label=SkillType.MANUAL_QA.value,
        section=SpecializationType.QA,
    ),
    SkillOptionView(
        value=SkillType.QA_AUTOMATION.value,
        label=SkillType.QA_AUTOMATION.value,
        section=SpecializationType.QA,
    ),
    SkillOptionView(
        value=SkillType.PERFORMANCE_TESTING.value,
        label=SkillType.PERFORMANCE_TESTING.value,
        section=SpecializationType.QA,
    ),
    SkillOptionView(
        value=SkillType.DEVOPS.value,
        label=SkillType.DEVOPS.value,
        section=SpecializationType.INFRASTRUCTURE_DEVOPS,
    ),
    SkillOptionView(
        value=SkillType.SRE.value,
        label=SkillType.SRE.value,
        section=SpecializationType.INFRASTRUCTURE_DEVOPS,
    ),
    SkillOptionView(
        value=SkillType.DBA.value,
        label=SkillType.DBA.value,
        section=SpecializationType.INFRASTRUCTURE_DEVOPS,
    ),
    SkillOptionView(
        value=SkillType.SYSTEM_ADMINISTRATION.value,
        label=SkillType.SYSTEM_ADMINISTRATION.value,
        section=SpecializationType.INFRASTRUCTURE_DEVOPS,
    ),
    SkillOptionView(
        value=SkillType.SQL.value,
        label=SkillType.SQL.value,
        section=SpecializationType.ANALYTICS,
    ),
    SkillOptionView(
        value=SkillType.DATA_ANALYSIS.value,
        label=SkillType.DATA_ANALYSIS.value,
        section=SpecializationType.ANALYTICS,
    ),
)


def _validate_skill_option_views() -> None:
    mapped_values = [item.value for item in _SKILL_OPTION_VIEWS]
    expected_values = [item.value for item in SkillType]

    if len(mapped_values) != len(set(mapped_values)):
        raise RuntimeError("Each SkillType must be mapped to exactly one mini-app UI section.")

    if set(mapped_values) != set(expected_values):
        raise RuntimeError("Mini-app skill UI sections must cover every SkillType exactly once.")

    unmapped_sections = {item.section for item in _SKILL_OPTION_VIEWS} - set(_SKILL_SECTION_ORDER)
    if unmapped_sections:
        raise RuntimeError("Mini-app skill UI sections must be declared in the section order.")


_validate_skill_option_views()

_WORK_FORMAT_LABELS = {
    WorkFormatChoice.ANY.value: "Любой",
    WorkFormat.REMOTE.value: "Удаленка",
    WorkFormat.HYBRID.value: "Гибрид",
    WorkFormat.ONSITE.value: "Офис",
}


def build_specialization_options() -> list[str]:
    return [item.value for item in SpecializationType]


def build_skill_options() -> list[str]:
    return [item.value for item in SkillType]


def build_skill_sections() -> list[SkillSectionView]:
    return [
        SkillSectionView(
            title=section_title.value,
            options=tuple(item for item in _SKILL_OPTION_VIEWS if item.section == section_title),
        )
        for section_title in _SKILL_SECTION_ORDER
    ]


def build_work_format_options() -> list[ChoiceOptionDto]:
    options = [
        ChoiceOptionDto(
            value=WorkFormatChoice.ANY.value,
            label=_WORK_FORMAT_LABELS[WorkFormatChoice.ANY.value],
        )
    ]
    options.extend(
        ChoiceOptionDto(value=item.value, label=_WORK_FORMAT_LABELS[item.value])
        for item in WorkFormat
        if item is not WorkFormat.UNDEFINED
    )
    return options


def _path_for(request: Request, name: str, **path_params: object) -> str:
    return str(request.app.url_path_for(name, **path_params))


def build_specialty_page_context(request: Request) -> dict[str, object]:
    return {
        "page_title": "Настройка специальностей",
        "page_description": "Добавьте или удалите нужные:",
        "active_page": "specialty",
        "selected_specializations": [],
        "selected_skills": [],
        "specialization_options": build_specialization_options(),
        "skill_sections": build_skill_sections(),
        "action_label": "Сохранить",
        "save_url": _path_for(request, "miniapp-save-specialty"),
        "success_text": "Специализации и скиллы сохранены.",
    }


def build_format_page_context(request: Request) -> dict[str, object]:
    return {
        "page_title": "Настройка формата",
        "page_description": "Выберите подходящий формат работы.",
        "active_page": "format",
        "current_value": "",
        "options": build_work_format_options(),
        "action_label": "Сохранить",
        "save_url": _path_for(request, "miniapp-save-format"),
        "success_text": "Формат сохранен.",
    }


def build_salary_page_context(request: Request) -> dict[str, object]:
    return {
        "page_title": "Настройка зарплаты",
        "page_description": "Выберите режим зарплаты и укажите сумму при необходимости.",
        "active_page": "salary",
        "salary_mode": "",
        "salary_amount": "",
        "action_label": "Сохранить",
        "save_url": _path_for(request, "miniapp-save-salary"),
        "success_text": "Зарплата сохранена.",
    }

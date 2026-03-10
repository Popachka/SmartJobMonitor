from fastapi import Request

from app.application.dto.miniapp import ChoiceOptionDto, WorkFormatChoice
from app.domain.shared.value_objects import SkillType, SpecializationType, WorkFormat


def build_specialization_options() -> list[str]:
    return [item.value for item in SpecializationType]


def build_skill_options() -> list[str]:
    return [item.value for item in SkillType]


def build_work_format_options() -> list[ChoiceOptionDto]:
    options = [ChoiceOptionDto(value=WorkFormatChoice.ANY.value, label=WorkFormatChoice.ANY.value)]
    options.extend(
        ChoiceOptionDto(value=item.value, label=item.value)
        for item in WorkFormat
        if item is not WorkFormat.UNDEFINED
    )
    return options


def build_specialty_page_context(request: Request) -> dict[str, object]:
    return {
        "page_title": "Настройка скиллов",
        "page_description": "Добавьте или уберите нужные специализации и скиллы.",
        "active_page": "specialty",
        "selected_specializations": [],
        "selected_skills": [],
        "specialization_options": build_specialization_options(),
        "skill_options": build_skill_options(),
        "action_label": "Сохранить",
        "save_url": str(request.url_for("miniapp-save-specialty")),
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
        "save_url": str(request.url_for("miniapp-save-format")),
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
        "save_url": str(request.url_for("miniapp-save-salary")),
        "success_text": "Зарплата сохранена.",
    }

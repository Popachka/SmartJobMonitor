from uuid import uuid4

import pytest

from app.domain.shared.value_objects import LanguageType, SpecializationType, WorkFormat
from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.exceptions import ValidationError


@pytest.fixture
def base_vacancy_params():
    """Базовый набор корректных параметров в соответствии с новой сигнатурой create"""
    return {
        "vacancy_id": uuid4(),
        "text": "Нужен Python разработчик в команду.",
        "specializations_raw": ["Backend"],
        "languages_raw": ["Python"],
        "tech_stack_raw": ["FastAPI", "PostgreSQL"],
        "min_experience_months": 12,
        "mirror_chat_id": 1,
        "mirror_message_id": 1,
        "work_format": WorkFormat.REMOTE,
        "salary_amount": 200000,
        "salary_currency": "RUB"
    }


def test_vacancy_create_success(base_vacancy_params):
    vacancy = Vacancy.create(**base_vacancy_params)

    assert vacancy.text == "Нужен Python разработчик в команду."
    assert SpecializationType.BACKEND in vacancy.specializations.items
    assert LanguageType.PYTHON in vacancy.primary_languages.items
    assert "Fastapi" in vacancy.tech_stack.items
    assert vacancy.salary.amount == 200000


def test_vacancy_content_hash_logic(base_vacancy_params):
    v1 = Vacancy.create(**base_vacancy_params)

    params2 = base_vacancy_params.copy()
    params2["text"] = "  НУЖЕН python РАЗРАБОТЧИК в команду. \n"
    v2 = Vacancy.create(**params2)

    assert v1.content_hash == v2.content_hash
    assert v1.content_hash.value is not None


def test_vacancy_fails_if_no_valid_specs(base_vacancy_params):
    params = base_vacancy_params.copy()
    params["specializations_raw"] = ["Chef", "Driver"]

    with pytest.raises(ValidationError):
        Vacancy.create(**params)


def test_vacancy_fails_if_no_valid_languages(base_vacancy_params):
    params = base_vacancy_params.copy()
    params["languages_raw"] = ["English", "Russian"]

    with pytest.raises(ValidationError):
        Vacancy.create(**params)


def test_vacancy_fails_if_text_is_empty(base_vacancy_params):
    params = base_vacancy_params.copy()

    params["text"] = ""
    with pytest.raises(ValidationError):
        Vacancy.create(**params)

    params["text"] = "   "
    with pytest.raises(ValidationError):
        Vacancy.create(**params)


def test_vacancy_normalizes_experience(base_vacancy_params):
    params = base_vacancy_params.copy()
    params["min_experience_months"] = -5

    vacancy = Vacancy.create(**params)
    assert vacancy.min_experience_months == 0

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.value_objects import (
    LanguageType,
    SpecializationType,
    VacancyId,
    WorkFormat,
)
from app.infrastructure.db.mappers.vacancy import (
    apply_vacancy,
    vacancy_from_model,
    vacancy_to_model,
)
from app.infrastructure.db.models import Vacancy as VacancyModel


def _make_domain_vacancy(*, salary_currency: str | None = "RUB") -> Vacancy:
    return Vacancy.create(
        vacancy_id=uuid4(),
        text="Backend developer",
        specializations_raw=[SpecializationType.BACKEND.value],
        languages_raw=[LanguageType.PYTHON.value],
        tech_stack_raw=["FastAPI", "PostgreSQL"],
        min_experience_months=24,
        mirror_chat_id=1,
        mirror_message_id=2,
        work_format=WorkFormat.REMOTE,
        salary_amount=15000,
        salary_currency=salary_currency,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_vacancy_to_model_serializes_fields() -> None:
    vacancy = _make_domain_vacancy()
    model = vacancy_to_model(vacancy)

    assert model.id == vacancy.id.value
    assert model.text == vacancy.text
    assert model.specializations == [SpecializationType.BACKEND.value]
    assert model.primary_languages == [LanguageType.PYTHON.value]
    assert set(model.tech_stack) == {"Fastapi", "Postgresql"}
    assert model.min_experience_months == 24
    assert model.mirror_chat_id == 1
    assert model.mirror_message_id == 2
    assert model.salary_amount == 15000
    assert model.salary_currency == "RUB"
    assert model.work_format == WorkFormat.REMOTE.value
    assert model.is_active is True


def test_vacancy_from_model_restores_domain() -> None:
    model = VacancyModel(
        id=uuid4(),
        text="Frontend developer",
        specializations=[SpecializationType.FRONTEND.value],
        primary_languages=[LanguageType.JAVASCRIPT.value],
        tech_stack=["React", "Vite"],
        min_experience_months=12,
        mirror_chat_id=10,
        mirror_message_id=20,
        content_hash="hash",
        salary_amount=None,
        salary_currency=None,
        work_format=WorkFormat.UNDEFINED.value,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        is_active=True,
    )
    vacancy = vacancy_from_model(model)

    assert vacancy.id == VacancyId(model.id)
    assert vacancy.text == "Frontend developer"
    assert vacancy.specializations.items == {SpecializationType.FRONTEND}
    assert vacancy.primary_languages.items == {LanguageType.JAVASCRIPT}
    assert vacancy.tech_stack.items == {"React", "Vite"}
    assert vacancy.salary.amount is None
    assert vacancy.salary.currency is None
    assert vacancy.work_format == WorkFormat.UNDEFINED


def test_apply_vacancy_updates_model() -> None:
    vacancy = _make_domain_vacancy()
    model = VacancyModel(
        id=vacancy.id.value,
        text="Old",
        specializations=[],
        primary_languages=[],
        tech_stack=[],
        min_experience_months=0,
        mirror_chat_id=0,
        mirror_message_id=0,
        content_hash="old",
        salary_amount=None,
        salary_currency=None,
        work_format=WorkFormat.UNDEFINED.value,
        created_at=vacancy.created_at,
        is_active=False,
    )

    apply_vacancy(model, vacancy)

    assert model.text == vacancy.text
    assert model.specializations == [SpecializationType.BACKEND.value]
    assert model.primary_languages == [LanguageType.PYTHON.value]
    assert set(model.tech_stack) == {"Fastapi", "Postgresql"}
    assert model.salary_amount == 15000
    assert model.salary_currency == "RUB"
    assert model.work_format == WorkFormat.REMOTE.value
    assert model.is_active is True


def test_vacancy_to_model_handles_missing_currency() -> None:
    vacancy = _make_domain_vacancy(salary_currency=None)
    model = vacancy_to_model(vacancy)

    assert model.salary_amount == 15000
    assert model.salary_currency is None

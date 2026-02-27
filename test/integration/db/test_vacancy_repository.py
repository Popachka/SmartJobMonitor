from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.value_objects import (
    ContentHash,
    LanguageType,
    SpecializationType,
    WorkFormat,
)
from app.infrastructure.db.models import Vacancy as VacancyModel
from app.infrastructure.db.repositories.vacancy_repository import VacancyRepository


def _make_vacancy(
    text: str,
    *,
    min_experience_months: int = 12,
    salary_amount: int | None = 10000,
    salary_currency: str | None = "RUB",
    work_format: WorkFormat = WorkFormat.REMOTE,
) -> Vacancy:
    return Vacancy.create(
        vacancy_id=uuid4(),
        text=text,
        specializations_raw=[SpecializationType.BACKEND.value],
        languages_raw=[LanguageType.PYTHON.value],
        tech_stack_raw=["FastAPI", "PostgreSQL"],
        min_experience_months=min_experience_months,
        mirror_chat_id=1,
        mirror_message_id=2,
        work_format=work_format,
        salary_amount=salary_amount,
        salary_currency=salary_currency,
    )


@pytest.mark.asyncio
async def test_add_and_get_by_id(session) -> None:
    vacancy = _make_vacancy(text=f"Backend developer {uuid4()}")
    repo = VacancyRepository(session)

    await repo.add(vacancy)
    await session.commit()

    found = await repo.get_by_id(vacancy.id)

    assert found is not None
    assert found.id == vacancy.id
    assert found.content_hash == vacancy.content_hash
    assert found.salary.amount == vacancy.salary.amount


@pytest.mark.asyncio
async def test_get_by_content_hash(session) -> None:
    vacancy = _make_vacancy(text=f"Backend developer {uuid4()}")
    repo = VacancyRepository(session)

    await repo.add(vacancy)
    await session.commit()

    found = await repo.get_by_content_hash(vacancy.content_hash)

    assert found is not None
    assert found.id == vacancy.id


@pytest.mark.asyncio
async def test_exists_by_content_hash(session) -> None:
    vacancy = _make_vacancy(text=f"Backend developer {uuid4()}")
    repo = VacancyRepository(session)

    await repo.add(vacancy)
    await session.commit()

    assert await repo.exists_by_content_hash(vacancy.content_hash) is True
    assert await repo.exists_by_content_hash(ContentHash("missing")) is False


@pytest.mark.asyncio
async def test_upsert_updates_existing_record(session) -> None:
    base_text = f"Backend developer {uuid4()}"
    vacancy = _make_vacancy(text=base_text, min_experience_months=12)
    repo = VacancyRepository(session)

    await repo.upsert(vacancy)
    await session.commit()

    updated = _make_vacancy(
        text=base_text,
        min_experience_months=36,
        salary_amount=25000,
        salary_currency="USD",
        work_format=WorkFormat.HYBRID,
    )
    await repo.upsert(updated)
    await session.commit()

    found = await repo.get_by_content_hash(vacancy.content_hash)

    assert found is not None
    assert found.id == vacancy.id
    assert found.min_experience_months == 36
    assert found.salary.amount == 25000
    assert found.salary.currency.name == "USD"
    assert found.work_format == WorkFormat.HYBRID

    result = await session.execute(
        select(func.count())
        .select_from(VacancyModel)
        .where(VacancyModel.content_hash == vacancy.content_hash.value)
    )
    assert result.scalar_one() == 1

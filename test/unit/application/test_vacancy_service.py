import pytest

from app.application.dto import InfoRawVacancy, OutVacancyParse
from app.application.services.vacancy_service import VacancyService
from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.value_objects import LanguageType, Salary, SpecializationType, VacancyId, WorkFormat


class FakeExtractor:
    def __init__(self, result: OutVacancyParse) -> None:
        self.result = result
        self.calls: list[str] = []

    async def parse_vacancy(self, text: str) -> OutVacancyParse:
        self.calls.append(text)
        return self.result


class FakeRepo:
    def __init__(self) -> None:
        self.upserted: Vacancy | None = None

    async def upsert(self, vacancy: Vacancy) -> None:
        self.upserted = vacancy


class FakeUoW:
    def __init__(self) -> None:
        self.vacancies = FakeRepo()
        self.entered = False

    async def __aenter__(self) -> "FakeUoW":
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return None


@pytest.mark.asyncio
async def test_parse_message_returns_none_for_non_vacancy() -> None:
    extractor = FakeExtractor(
        OutVacancyParse(
            is_vacancy=False,
            specializations=[],
            primary_languages=[],
            min_experience_months=0,
            tech_stack=[],
        )
    )
    service = VacancyService(FakeUoW(), extractor)

    result = await service.parse_message(InfoRawVacancy(text="Not a vacancy"))

    assert result is None


@pytest.mark.asyncio
async def test_parse_message_returns_result_for_vacancy() -> None:
    parsed = OutVacancyParse(
        is_vacancy=True,
        specializations=[SpecializationType.BACKEND],
        primary_languages=[LanguageType.PYTHON],
        min_experience_months=12,
        tech_stack=["FastAPI"],
    )
    extractor = FakeExtractor(parsed)
    service = VacancyService(FakeUoW(), extractor)

    result = await service.parse_message(InfoRawVacancy(text="Vacancy text"))

    assert result == parsed


@pytest.mark.asyncio
async def test_parse_message_skips_empty_text() -> None:
    extractor = FakeExtractor(
        OutVacancyParse(
            is_vacancy=True,
            specializations=[],
            primary_languages=[],
            min_experience_months=0,
            tech_stack=[],
        )
    )
    service = VacancyService(FakeUoW(), extractor)

    result = await service.parse_message(InfoRawVacancy(text="  "))

    assert result is None
    assert extractor.calls == []


@pytest.mark.asyncio
async def test_save_vacancy_upserts_and_returns_id() -> None:
    parsed = OutVacancyParse(
        is_vacancy=True,
        specializations=[SpecializationType.BACKEND],
        primary_languages=[LanguageType.PYTHON],
        min_experience_months=12,
        tech_stack=["FastAPI"],
    )
    uow = FakeUoW()
    service = VacancyService(uow, FakeExtractor(parsed))

    result = await service.save_vacancy(
        raw_vacancy_info=InfoRawVacancy(
            text="Vacancy text",
            mirror_chat_id=1,
            mirror_message_id=2,
        ),
        parse_result=parsed,
    )

    assert isinstance(result, VacancyId)
    assert uow.vacancies.upserted is not None
    assert uow.vacancies.upserted.work_format == WorkFormat.UNDEFINED
    assert uow.vacancies.upserted.content_hash.value


@pytest.mark.asyncio
async def test_save_vacancy_raises_on_empty_text() -> None:
    parsed = OutVacancyParse(
        is_vacancy=True,
        specializations=[SpecializationType.BACKEND],
        primary_languages=[LanguageType.PYTHON],
        min_experience_months=12,
        tech_stack=["FastAPI"],
    )
    service = VacancyService(FakeUoW(), FakeExtractor(parsed))

    with pytest.raises(ValueError):
        await service.save_vacancy(
            raw_vacancy_info=InfoRawVacancy(text="  ", mirror_chat_id=1, mirror_message_id=2),
            parse_result=parsed,
        )


@pytest.mark.asyncio
async def test_save_vacancy_raises_when_mirror_ids_missing() -> None:
    parsed = OutVacancyParse(
        is_vacancy=True,
        specializations=[SpecializationType.BACKEND],
        primary_languages=[LanguageType.PYTHON],
        min_experience_months=12,
        tech_stack=["FastAPI"],
    )
    service = VacancyService(FakeUoW(), FakeExtractor(parsed))

    with pytest.raises(ValueError):
        await service.save_vacancy(
            raw_vacancy_info=InfoRawVacancy(text="Vacancy"),
            parse_result=parsed,
        )


@pytest.mark.asyncio
async def test_save_vacancy_maps_parse_result_fields() -> None:
    parsed = OutVacancyParse(
        is_vacancy=True,
        specializations=[SpecializationType.BACKEND, SpecializationType.FRONTEND],
        primary_languages=[LanguageType.PYTHON, LanguageType.JAVASCRIPT],
        min_experience_months=24,
        tech_stack=["FastAPI", "PostgreSQL"],
        salary=Salary.create(amount=15000, currency="RUB"),
        work_format=WorkFormat.REMOTE,
    )
    uow = FakeUoW()
    service = VacancyService(uow, FakeExtractor(parsed))

    await service.save_vacancy(
        raw_vacancy_info=InfoRawVacancy(
            text="Vacancy text",
            mirror_chat_id=1,
            mirror_message_id=2,
        ),
        parse_result=parsed,
    )

    assert uow.vacancies.upserted is not None
    vacancy = uow.vacancies.upserted
    assert vacancy.specializations.items == {
        SpecializationType.BACKEND,
        SpecializationType.FRONTEND,
    }
    assert vacancy.primary_languages.items == {
        LanguageType.PYTHON,
        LanguageType.JAVASCRIPT,
    }
    assert vacancy.min_experience_months == 24
    assert vacancy.tech_stack.items == {"Fastapi", "Postgresql"}
    assert vacancy.salary.amount == 15000
    assert vacancy.salary.currency.name == "RUB"
    assert vacancy.work_format == WorkFormat.REMOTE

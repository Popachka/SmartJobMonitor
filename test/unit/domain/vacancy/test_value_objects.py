import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError
from app.domain.vacancy.value_objects import (
    Specializations, SpecializationType,
    PrimaryLanguages, LanguageType,
    Salary, TechStack, VacancyId, CurrencyType
)


def test_specializations_filtering():
    raw_from_llm = ["Backend", "  Frontend  ", "PizzaMaker"]
    specs = Specializations.from_strs(raw_from_llm)

    assert len(specs.items) == 2
    assert SpecializationType.BACKEND in specs.items
    assert SpecializationType.FRONTEND in specs.items
    assert all(isinstance(item, SpecializationType) for item in specs.items)


def test_primary_languages_filtering():
    raw = ["Python", "Rust", "Lisp"]
    langs = PrimaryLanguages.from_strs(raw)

    assert len(langs.items) == 2
    assert LanguageType.PYTHON in langs.items
    assert LanguageType.RUST in langs.items


def test_salary_creation_and_validation():
    s = Salary.create(amount=150000, currency=" usd ")
    assert s.min_amount == 150000
    assert s.currency == CurrencyType.USD

    s_default = Salary.create(amount=100)
    assert s_default.currency == CurrencyType.RUB

    with pytest.raises(ValueError, match="cannot be negative"):
        Salary.create(amount=-100)


def test_tech_stack_normalization_via_factory():
    raw_stack = [" Python", "fastapi ", "PYTHON", "  ", "python"]
    stack = TechStack.create(raw_stack)

    assert "Python" in stack.items
    assert "Fastapi" in stack.items
    assert len(stack.items) == 2
    assert all(isinstance(item, str) for item in stack.items)

# --- Тесты на Immutability (защита данных) ---


def test_vo_immutability():
    v_id = VacancyId(value=uuid4())
    stack = TechStack.create(["Python"])
    salary = Salary.create(100)

    with pytest.raises(FrozenInstanceError):
        v_id.value = uuid4()

    with pytest.raises(FrozenInstanceError):
        stack.items = frozenset(["Java"])

    with pytest.raises(FrozenInstanceError):
        salary.min_amount = 200

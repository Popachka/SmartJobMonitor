from datetime import UTC, datetime
from uuid import uuid4

from app.domain.shared import WorkFormat
from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode
from app.domain.vacancy.entities import Vacancy
from app.infrastructure.db.mappers.user import user_from_model, user_to_model
from app.infrastructure.db.mappers.vacancy import vacancy_from_model, vacancy_to_model


def test_user_mapper_round_trip_preserves_skills() -> None:
    user = User.create(
        tg_id=123,
        username="alice",
        cv_text="resume text",
        cv_specializations_raw=["Backend"],
        cv_skills_raw=["Python", "React"],
        filter_salary_mode=FilterMode.SOFT,
        filter_work_format_mode=FilterMode.SOFT,
    )

    model = user_to_model(user)
    restored = user_from_model(model)

    assert sorted(model.cv_skills) == ["Python", "React"]
    assert sorted(item.value for item in restored.cv_skills.items) == ["Python", "React"]


def test_vacancy_mapper_round_trip_preserves_skills() -> None:
    vacancy = Vacancy.create(
        vacancy_id=uuid4(),
        text="Frontend engineer with React",
        specializations_raw=["Frontend"],
        skills_raw=["React", "JavaScript"],
        mirror_chat_id=100,
        mirror_message_id=200,
        work_format=WorkFormat.REMOTE,
        created_at=datetime.now(UTC),
    )

    model = vacancy_to_model(vacancy)
    restored = vacancy_from_model(model)

    assert sorted(model.skills) == ["JavaScript", "React"]
    assert sorted(item.value for item in restored.skills.items) == ["JavaScript", "React"]

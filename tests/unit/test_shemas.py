import pytest

from src.infrastructure.shemas import CandidateCriteria, VacancyData, UserData, UserResumeUpdateDTO

@pytest.mark.unit
def test_vacancy_data_coerces_lists():
    data = VacancyData.model_validate({
        "id": 1,
        "text": "text",
        "specializations": None,
        "primary_languages": None,
        "min_experience_months": 0,
        "tech_stack": None,
        "mirror_chat_id": 1,
        "mirror_message_id": 2,
    })
    assert data.specializations == []
    assert data.primary_languages == []
    assert data.tech_stack == []

@pytest.mark.unit
def test_user_data_coerces_lists():
    data = UserData.model_validate({
        "id": 1,
        "tg_id": 123,
        "text_resume": "resume",
        "specializations": None,
        "primary_languages": None,
        "experience_months": 0,
        "tech_stack": None,
    })
    assert data.specializations == []
    assert data.primary_languages == []
    assert data.tech_stack == []

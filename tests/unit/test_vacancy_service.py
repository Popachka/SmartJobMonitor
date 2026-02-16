import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from pytest import MonkeyPatch

from src.services.vacancy_service import VacancyService
from src.infrastructure.agents.vacancy import OutVacancyParse
from src.infrastructure.shemas import MessageInfo


@pytest.mark.asyncio
async def test_vacancy_service_returns_none_if_not_vacancy():
    """
    Проверяем, что если агент пометил сообщение как 'не вакансия', 
    сервис возвращает None и не идет в базу данных.
    """
    # 1. Подготавливаем фейковый результат парсинга от LLM
    fake_parse_result = OutVacancyParse(
        is_vacancy=False,  # Ключевой триггер для теста
        specializations=[],
        primary_languages=[],
        min_experience_months=0,
        tech_stack=[]
    )

    # 2. Настраиваем мок агента
    mock_agent = AsyncMock()
    # Имитируем структуру pydantic_ai: result.output
    mock_agent.run.return_value = MagicMock(output=fake_parse_result)

    # 3. Инициализируем сервис
    # Передаем AsyncMock в фабрику сессий, чтобы вызов с async with сработал
    service = VacancyService(session_factory=AsyncMock())
    service._agent = mock_agent  # Инъекция мока (Dependency Injection)

    # 4. Создаем входные данные сообщения
    message = MessageInfo(
        text="Просто привет, это не вакансия",
        mirror_chat_id=123456,
        mirror_message_id=789
    )

    # 5. Выполняем действие
    result = await service.process_vacancy_message(message)

    # 6. Проверки
    assert result is None
    mock_agent.run.assert_called_once()  # Убеждаемся, что агент вызывался


@pytest.mark.asyncio
async def test_process_vacancy_success():
    # 1. Данные от LLM
    fake_parse = OutVacancyParse(
        is_vacancy=True,
        specializations=["Backend"],
        primary_languages=["Python"],
        min_experience_months=12,
        tech_stack=["FastAPI", "PostgreSQL"]
    )
    mock_agent = AsyncMock()
    mock_agent.run.return_value = MagicMock(output=fake_parse)

    # 2. Мокаем репозиторий и сессию
    mock_vacancy = MagicMock()
    mock_vacancy.id = 99

    # Чтобы мокать VacancyRepository внутри асинхронного контекстного менеджера,
    # нам нужно подменить сам класс или метод create через patch
    with patch("src.services.vacancy_service.VacancyRepository") as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.create = AsyncMock(return_value=mock_vacancy)

        service = VacancyService(session_factory=AsyncMock())
        service._agent = mock_agent

        message = MessageInfo(
            text="Python Dev", mirror_chat_id=1, mirror_message_id=1)

        # 3. Action
        result = await service.process_vacancy_message(message)

        # 4. Asserts
        assert result == 99
        # Проверяем, что в репозиторий ушло правильное DTO
        args, _ = repo_instance.create.call_args
        dto = args[0]
        assert dto.text == "Python Dev"
        assert dto.min_experience_months == 12


@pytest.mark.asyncio
async def test_process_vacancy_empty_text():
    service = VacancyService(session_factory=AsyncMock())
    # Агент не должен быть вызван вообще
    service._agent = AsyncMock()

    message = MessageInfo(text="", mirror_chat_id=1, mirror_message_id=1)
    result = await service.process_vacancy_message(message)

    assert result is None
    service._agent.run.assert_not_called()


@pytest.mark.asyncio
async def test_process_vacancy_agent_error():
    mock_agent = AsyncMock()
    mock_agent.run.side_effect = Exception("LLM Timeout")

    service = VacancyService(session_factory=AsyncMock())
    service._agent = mock_agent

    message = MessageInfo(
        text="Valid text", mirror_chat_id=1, mirror_message_id=1)

    with pytest.raises(Exception, match="LLM Timeout"):
        await service.process_vacancy_message(message)

# Описание задач (parse_vacancy, match_job)
import asyncio
from src.infrastructure.tkq import broker
from src.infrastructure.db import async_session
from src.repositories.vacancy_repository import VacancyRepository
from src.schemas.vacancy import VacancyParsedSchema
from src.infrastructure.logger import get_app_logger

logger = get_app_logger(__name__)

@broker.task
async def parse_vacancy_task(raw_id: int):
    """Задача: получить сырую вакансию, прогнать через AI и сохранить."""
    logger.info(f"Начинаем парсинг вакансии ID: {raw_id}")

    async with async_session() as session:
        repo = VacancyRepository(session)

        # 1. Заглушка имитации работы AI
        await asyncio.sleep(2)

        # Представим, что это вернул наш агент
        mock_data = VacancyParsedSchema(
            title="Backend Developer (Mock)",
            tech_stack=["Python", "PostgreSQL", "Redis"],
        )

        # 2. Сохраняем структурированные данные
        parsed_vacancy = await repo.save_parsed_vacancy(raw_id, mock_data)
        logger.info(
            f"Вакансия {raw_id} сохранена в структурированном виде. ID: {parsed_vacancy.id}"
        )

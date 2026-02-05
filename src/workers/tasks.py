# Описание задач (parse_vacancy, match_job)
import asyncio
from src.core.tkq import broker
from src.core.db import async_session
from src.services.vacancy_service import VacancyService
from src.schemas.vacancy import VacancyParsedSchema
from src.core.logger import get_app_logger
from src.services.user_service import UserService
from src.schemas.user import ResumeParsedSchema
from src.services.matcher_service import MatchService
from src.bot.main import Bot
from src.core.config import config

logger = get_app_logger(__name__)

@broker.task
async def parse_vacancy_task(raw_id: int):
    """Задача: получить сырую вакансию, прогнать через AI и сохранить."""
    logger.info(f"Начинаем парсинг вакансии ID: {raw_id}")

    async with async_session() as session:
        service = VacancyService(session)
        
        # 1. Заглушка имитации работы AI
        await asyncio.sleep(2)
        
        # Представим, что это вернул наш агент
        mock_data = VacancyParsedSchema(
            title="Backend Developer (Mock)",
            tech_stack=["Python", "PostgreSQL", "Redis"],
        )
        
        # 2. Сохраняем структурированные данные
        parsed_vacancy = await service.save_parsed_vacancy(raw_id, mock_data)
        logger.info(f"Вакансия {raw_id} сохранена в структурированном виде. ID: {parsed_vacancy.id}")
        
        # 3. Отправляем на матчинг именно ID распарсенной вакансии
    await match_users_task.kiq(parsed_vacancy.id)
@broker.task
async def match_users_task(vacancy_id: int):
    """Задача: найти юзеров, которым подходит вакансия."""
    logger.info(f"Начинаем поиск кандидатов для вакансии ID: {vacancy_id}")
    
    async with async_session() as session:
        match_service = MatchService(session)
        matched_users = await match_service.get_matching_users(vacancy_id)
        
        if not matched_users:
            logger.info(f"Подходящих юзеров для вакансии {vacancy_id} не найдено.")
            return
    # для каждого подходящего юзера создать запрос к LLM

@broker.task
async def parse_resume_task(tg_id: int, text: str):
    """Задача: парсинг резюме пользователя через LLM."""
    logger.info(f"Начинаем парсинг резюме для юзера {tg_id}")

    async with async_session() as session:
        user_service = UserService(session)
        
        # 1. (Заглушка) Имитация работы AI агента для резюме
        import asyncio
        await asyncio.sleep(3)
        
        # Представим, что это вытащил агент
        mock_resume_data = ResumeParsedSchema(
            tech_stack=["Python", "SQL", "Docker"],
        )
        
        # 2. Обновляем данные пользователя в БД
        await user_service.update_resume(
            tg_id=tg_id,
            text=text,
            parsed_data=mock_resume_data
        )
        
        logger.info(f"Профиль пользователя {tg_id} успешно обновлен.")
        
        # 3. (Опционально) Можно отправить сообщение пользователю через бота
        # Для этого воркеру понадобится экземпляр Bot
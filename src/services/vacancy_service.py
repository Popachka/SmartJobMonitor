from src.infrastructure.agents.vacancy import OutVacancyParse, get_vacancy_parse_agent
from src.infrastructure.logger import get_app_logger
from src.repositories.vacancy_repository import VacancyRepository
from src.infrastructure.shemas import MessageInfo, VacancyCreateDTO
import time
logger = get_app_logger(__name__)


class VacancyService:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._agent = get_vacancy_parse_agent()

    async def process_message(self, message_info: MessageInfo) -> int | None:
        parse_result = await self._extract_entity(message_info)
        if not parse_result.is_vacancy or not message_info.text:
            logger.info("Сообщение не является вакансией")
            return None

        vacancy_dto = VacancyCreateDTO(
            text=message_info.text,
            specializations=parse_result.specializations,
            primary_languages=parse_result.primary_languages,
            min_experience_months=parse_result.min_experience_months,
            tech_stack=parse_result.tech_stack,
            mirror_chat_id=message_info.mirror_chat_id,
            mirror_message_id=message_info.mirror_message_id,
        )
        async with self.session_factory() as session:
            vacancy_repo = VacancyRepository(session)
            vacancy = await vacancy_repo.create_vacancy(vacancy_dto)
            return vacancy.id

    async def _extract_entity(self, message_info: MessageInfo) -> OutVacancyParse:
        start_ts = time.monotonic()

        logger.info("Vacancy parsing started")
        prompt = f"Текст вакансии:\n{message_info.text}"
        result = await self._agent.run(user_prompt=prompt)
        duration = time.monotonic() - start_ts
        logger.info(
            f"Vacancy parsing finished duration_sec: {round(duration, 3)}")
        return result.output

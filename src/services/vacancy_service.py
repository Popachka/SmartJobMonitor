from src.infrastructure.agents.vacancy import OutVacancyParse, get_vacancy_parse_agent
from src.infrastructure.logger import get_app_logger, trace_performance
from src.repositories.vacancy_repository import VacancyRepository
from src.infrastructure.shemas import MessageInfo, VacancyCreateDTO
import time
logger = get_app_logger(__name__)


class VacancyService:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._agent = get_vacancy_parse_agent()

    async def process_vacancy_message(self, message_info: MessageInfo) -> int | None:
        parse_result = await self._parse_vacancy(message_info)
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
            vacancy = await vacancy_repo.create(vacancy_dto)
            return vacancy.id

    @trace_performance("Vacancy: extract entities")
    async def _parse_vacancy(self, message_info: MessageInfo) -> OutVacancyParse:
        prompt = f"Текст вакансии:\n{message_info.text}"
        result = await self._agent.run(user_prompt=prompt)
        return result.output

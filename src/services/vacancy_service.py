from src.infrastructure.agents.vacancy import OutVacancyParse, get_vacancy_parse_agent
from src.infrastructure.logger import get_app_logger, trace_performance
from src.repositories.vacancy_repository import VacancyRepository
from src.infrastructure.shemas import MessageInfo, VacancyCreateDTO
from src.infrastructure.metrics import track
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_app_logger(__name__)


class VacancyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._agent = get_vacancy_parse_agent()

    async def parse_message(self, message_info: MessageInfo) -> OutVacancyParse | None:
        async with track("vacancy.parse_llm"):
            prompt = f"Текст вакансии:\n{message_info.text}"
            result = await self._agent.run(user_prompt=prompt)
            parse_result = result.output

            if not parse_result.is_vacancy:
                logger.info("Message is not a vacancy")
                return None
            return parse_result

    async def save_vacancy(self, message_info: MessageInfo, parse_result: OutVacancyParse) -> int:
        vacancy_dto = VacancyCreateDTO(
            text=message_info.text,
            specializations=parse_result.specializations,
            primary_languages=parse_result.primary_languages,
            min_experience_months=parse_result.min_experience_months,
            tech_stack=parse_result.tech_stack,
            mirror_chat_id=message_info.mirror_chat_id,
            mirror_message_id=message_info.mirror_message_id,
        )
        vacancy_repo = VacancyRepository(self.session)
        vacancy = await vacancy_repo.create(vacancy_dto)
        return vacancy.id

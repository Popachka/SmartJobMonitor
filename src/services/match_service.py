from src.infrastructure.agents.match import OutMatchParse, get_match_agent
from src.bot.notifier import BotNotifier
from src.infrastructure.logger import get_app_logger, trace_performance
from src.repositories.match_repository import MatchRepository
from src.repositories.user_repository import UserRepository
from src.infrastructure.shemas import VacancyData, UserData, CandidateCriteria
from src.repositories.vacancy_repository import VacancyRepository
from sqlalchemy.ext.asyncio import AsyncSession
import time
from src.infrastructure.exceptions import VacancyNotFoundError
from src.infrastructure.metrics import track
logger = get_app_logger(__name__)


class MatchService:
    def __init__(self, session: AsyncSession, notifier: BotNotifier | None = None):
        self.session = session
        self.notifier = notifier
        self._agent = get_match_agent()

    async def get_potential_candidates(self, vacancy_id: int) -> tuple[VacancyData, list[UserData]]:
        v_repo = VacancyRepository(self.session)
        u_repo = UserRepository(self.session)

        vacancy_model = await v_repo.get_by_id(vacancy_id)
        if not vacancy_model:
            logger.error(f"Vacancy {vacancy_id} not found in database")
            raise VacancyNotFoundError

        experience_threshold = int(vacancy_model.min_experience_months * 0.8)

        criteria = CandidateCriteria(
            min_experience_months=experience_threshold,
            match_specializations=vacancy_model.specializations,
            match_languages=vacancy_model.primary_languages,
            match_mode="and",
        )
        user_models = await u_repo.find_candidates(criteria)

        vacancy_dto = VacancyData.model_validate(vacancy_model)
        candidates_dto = [UserData.model_validate(
            user) for user in user_models]

        return vacancy_dto, candidates_dto

    async def score_match(self, vacancy: VacancyData, user: UserData) -> OutMatchParse:
        return await self._score_vacancy_resume(
            vacancy_text=vacancy.text,
            resume_text=user.text_resume,
        )

    async def save_match(self, vacancy: VacancyData, user: UserData, score: int) -> None:
        match_repo = MatchRepository(self.session)
        await match_repo.create(
            vacancy_id=vacancy.id,
            user_id=user.id,
            score=score,
        )

    async def notify_match(self, vacancy: VacancyData, user: UserData, score: int) -> None:
        if not self.notifier:
            return
        await self.notifier.send_match(
            user_tg_id=user.tg_id,
            mirror_chat_id=vacancy.mirror_chat_id,
            mirror_message_id=vacancy.mirror_message_id,
            score=score,
        )

    @trace_performance("Score_match")
    async def _score_vacancy_resume(self, vacancy_text: str, resume_text: str) -> OutMatchParse:
        prompt = (
            "Vacancy:\n"
            f"{vacancy_text}\n\n"
            "Resume:\n"
            f"{resume_text}"
        )
        result = await self._agent.run(user_prompt=prompt)
        return result.output

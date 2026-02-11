from src.infrastructure.agents.match import OutMatchParse, get_match_agent
from src.bot.notifier import BotNotifier
from src.infrastructure.logger import get_app_logger
from src.repositories.match_repository import MatchRepository
from src.repositories.user_repository import UserRepository
from src.infrastructure.shemas import VacancyData, UserData, CandidateCriteria
from src.repositories.vacancy_repository import VacancyRepository
import time
from src.infrastructure.exceptions import VacancyNotFoundError
logger = get_app_logger(__name__)


class MatchService:
    def __init__(self, session_factory, notifier: BotNotifier):
        self.session_factory = session_factory
        self.notifier = notifier
        self._agent = get_match_agent()

    async def process_vacancy(self, vacancy_id: int) -> None:
        async with self.session_factory() as session:
            v_repo = VacancyRepository(session)
            u_repo = UserRepository(session)

            vacancy = await v_repo.get_by_id(vacancy_id)
            if not vacancy:
                raise VacancyNotFoundError
            criteria = CandidateCriteria(
                min_experience_months=int(vacancy.min_experience_months * 0.8),
                match_specializations=vacancy.specializations,
                match_languages=vacancy.primary_languages,
                match_mode="and",
            )
            users = await u_repo.find_candidates(criteria)
            vacancy_data = VacancyData.model_validate(vacancy)
            candidates = [UserData.model_validate(u) for u in users]

        for user_data in candidates:
            try:
                logger.info(f'Send vacancy to {user_data.tg_id}')
                await self._process_single_match(vacancy_data, user_data)
            except Exception as e:
                logger.error(f"Ошибка матчинга для юзера {user_data.id}: {e}")

    async def _process_single_match(self, vacancy: VacancyData, user: UserData) -> None:

        resume_text = user.text_resume
        score_result = await self._score_match(vacancy_text=vacancy.text, resume_text=resume_text)

        async with self.session_factory() as session:
            match_repo = MatchRepository(session)
            await match_repo.create_match(
                vacancy_id=vacancy.id,
                user_id=user.id,
                score=score_result.score,
            )

        await self.notifier.send_match(
            user_tg_id=user.tg_id,
            mirror_chat_id=vacancy.mirror_chat_id,
            mirror_message_id=vacancy.mirror_message_id,
            score=score_result.score,
        )

    async def _score_match(self, vacancy_text: str, resume_text: str) -> OutMatchParse:
        start_ts = time.monotonic()

        logger.info("Match scoring started")
        prompt = (
            "Vacancy:\n"
            f"{vacancy_text}\n\n"
            "Resume:\n"
            f"{resume_text}"
        )
        result = await self._agent.run(user_prompt=prompt)
        if not isinstance(result.output, OutMatchParse):
            raise ValueError("Match parse returned invalid type")

        duration = time.monotonic() - start_ts
        logger.info(
            f"Match scoring finished duration_sec: {round(duration, 3)}")
        return result.output

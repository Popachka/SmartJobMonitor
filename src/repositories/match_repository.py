                          
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.logger import get_app_logger
from src.models.match import VacancyMatch

logger = get_app_logger(__name__)


class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, match_id: int) -> VacancyMatch | None:
        return await self.session.get(VacancyMatch, match_id)

    async def create(
        self,
        vacancy_id: int,
        user_id: int,
        score: int,
    ) -> VacancyMatch:
        try:
            match = VacancyMatch(
                vacancy_id=vacancy_id,
                user_id=user_id,
                score=score,
            )
            self.session.add(match)
            await self.session.commit()
            await self.session.refresh(match)
            return match
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save match: {e}")
            raise

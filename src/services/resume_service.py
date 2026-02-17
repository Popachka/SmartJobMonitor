from src.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.agents.resume import OutResumeParse
from src.infrastructure.parsers import BaseResumeParser, ParserInput
from src.infrastructure.exceptions import NotAResumeError
from src.infrastructure.logger import get_app_logger
from src.infrastructure.shemas import UserResumeUpdateDTO
from src.infrastructure.metrics import track

logger = get_app_logger(__name__)


class ResumeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=session)

    async def parse_resume(self, source: ParserInput, parser: BaseResumeParser) -> UserResumeUpdateDTO:
        async with track("resume.process"):
            data: OutResumeParse = await parser.extract_text(source)
            if not data.is_resume:
                raise NotAResumeError()
            return UserResumeUpdateDTO(
                specializations=data.specializations,
                primary_languages=data.primary_languages,
                experience_months=data.experience_months,
                tech_stack=data.tech_stack,
                text_resume=data.full_relevant_text_from_resume,
            )

    async def save_resume(self, tg_id: int, dto: UserResumeUpdateDTO) -> None:
        logger.info(f"Updating user profile {tg_id}")
        await self.user_repo.update_resume_by_tg_id(tg_id=tg_id, dto=dto)


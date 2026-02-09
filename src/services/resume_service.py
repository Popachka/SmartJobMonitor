from src.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.agents.resume import OutResumeParse
from src.infrastructure.parsers import BaseResumeParser, ParserInput
from src.infrastructure.exceptions import NotAResumeError
from src.infrastructure.logger import get_app_logger

logger = get_app_logger(__name__)

class ResumeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=session)

    async def process_resume(self, source: ParserInput, parser: BaseResumeParser, tg_id: int) -> None:
        data: OutResumeParse = await parser.extract_text(source)
        if not data.is_resume:
            raise NotAResumeError()
        logger.info(f"Обновление резюме для пользователя {tg_id}")
        await self.user_repo.update_user_resume(tg_id=tg_id, data=data)

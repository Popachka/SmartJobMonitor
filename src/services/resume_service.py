from src.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.agents.resume import OutResumeParse
from src.infrastructure.parsers import BaseResumeParser, ParserInput


class ResumeService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session=session)

    async def process_resume(self, source: ParserInput, parser: BaseResumeParser) -> OutResumeParse:
        data = await parser.extract_text(source)

        return data

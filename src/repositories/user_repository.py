from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.infrastructure.logger import get_app_logger
from src.agents.resume import OutResumeParse

logger = get_app_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_or_create_user(self, tg_id: int, username: str | None = None) -> User:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            logger.info(f"Юзер {tg_id} не найден. Создаем новую запись...")
            user = User(tg_id=tg_id, username=username)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Юзер {tg_id} успешно сохранен с ID {user.id}")
        else:
            logger.info(f"Юзер {tg_id} уже существует (ID {user.id})")

        return user

    async def update_user_resume(self, tg_id: int, data: "OutResumeParse"):
        if not data.is_resume:
            logger.warning(f"Попытка обновить резюме для {tg_id}, но в данных is_resume=False. Пропускаем.")
            return None
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            user.text_resume = data.full_relevant_text_from_resume
            user.tech_stack = data.tech_stack
            user.main_programming_language = data.main_programming_language
            await self.session.commit()
        return user

    async def get_users_by_main_programming_language(self, lang: str) -> list[User]:
        if not lang:
            return []
        query = select(User).where(
            User.main_programming_language == lang,
            User.text_resume.is_not(None),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

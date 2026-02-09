from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.infrastructure.logger import get_app_logger

logger = get_app_logger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def update_resume(self, tg_id: int, text: str):
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            user.text_resume = text
            # user.tech_stack = parsed_data.tech_stack
            # user.primary_language = parsed_data.primary_language
            await self.session.commit()
        return user

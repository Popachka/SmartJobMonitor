from sqlalchemy import select, and_, or_, false, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import array
from src.models.user import User
from src.infrastructure.logger import get_app_logger
from src.infrastructure.shemas import UserResumeUpdateDTO, CandidateCriteria


logger = get_app_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_by_tg_id(self, tg_id: int, username: str | None = None) -> User:
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

    async def update_resume_by_tg_id(self, tg_id: int, dto: UserResumeUpdateDTO) -> User | None:
        query = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            for key, value in dto.model_dump().items():
                setattr(user, key, value)

            try:
                await self.session.commit()
                await self.session.refresh(user)
            except Exception as e:
                await self.session.rollback()
                logger.error(f"Error updating user {tg_id}: {e}")
                raise
        return user

    async def find_candidates(self, criteria: CandidateCriteria) -> list[User]:
        clauses = [User.text_resume.is_not(None)]
        spec_clause = (
            User.specializations.op("?|")(array(criteria.match_specializations or [], type_=Text))
            if criteria.match_specializations else false()
        )
        lang_clause = (
            User.primary_languages.op("?|")(array(criteria.match_languages or [], type_=Text))
            if criteria.match_languages else false()
        )

        if criteria.match_mode == "or":
            clauses.append(or_(spec_clause, lang_clause))
        else:
            clauses.append(and_(spec_clause, lang_clause))

        clauses.append(User.experience_months >=
                       criteria.min_experience_months)

        query = select(User).where(and_(*clauses))
        result = await self.session.execute(query)
        return list(result.scalars().all())

from app.application.ports.unit_of_work import UserUnitOfWork
from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode, UserId, WorkFormat


class UserService:
    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def upsert_user(self, tg_id: int, username: str | None) -> User:
        user = User.create(tg_id=tg_id, username=username)
        async with self._uow:
            await self._uow.users.upsert(user)
        return user

    async def update_filters(
        self,
        tg_id: int,
        experience_mode: FilterMode,
        salary_mode: FilterMode,
        work_format: WorkFormat | None,
        work_format_mode: FilterMode,
    ) -> bool:
        async with self._uow:
            user = await self._uow.users.get_by_tg_id(UserId(tg_id))
            if user is None:
                return False
            user.filter_experience_mode = experience_mode
            user.filter_salary_mode = salary_mode
            user.cv_work_format = work_format
            user.filter_work_format_mode = work_format_mode
            await self._uow.users.update(user)
        return True

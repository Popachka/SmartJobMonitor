from typing import Any, Awaitable, Callable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.logger import get_app_logger
from app.domain.user.value_objects import UserId
from app.infrastructure.db import UserUnitOfWork
from app.telegram.bot.keyboards import START_BUTTON_TEXT, get_start_kb

logger = get_app_logger(__name__)


class UserGuardMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        if event.from_user is None:
            logger.warning("Message without from_user received, skipping")
            return None

        text = (event.text or "").strip()
        if text.startswith("/start") or text == START_BUTTON_TEXT:
            return await handler(event, data)

        uow = UserUnitOfWork(self._session_factory)
        async with uow:
            user = await uow.users.get_by_tg_id(UserId(event.from_user.id))

        if user is None:
            await event.answer(
                "Нажмите «Начать пользоваться ботом», чтобы продолжить.",
                reply_markup=get_start_kb(),
            )
            return None

        return await handler(event, data)

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.application.services.user_service import UserService
from app.core.logger import get_app_logger
from app.infrastructure.db import UserUnitOfWork, async_session_factory
from app.telegram.bot.keyboards import START_BUTTON_TEXT, get_main_menu_kb
from app.telegram.bot.states import BotStates

router = Router()
logger = get_app_logger(__name__)

AVAILABLE_COMMANDS_TEXT = (
    "/settings — изменить настройки ленты вакансий\n"
    "/profile — проверить свой профиль\n"
    "/help — как это работает"
)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        logger.warning("Received /start without from_user; skipping")
        await state.clear()
        return

    user_id = message.from_user.id
    logger.info(f"Started onboarding for user {user_id}")

    uow = UserUnitOfWork(async_session_factory)
    service = UserService(uow)
    try:
        user, is_new = await service.get_or_create_user(
            tg_id=user_id,
            username=message.from_user.username,
        )
        logger.info(f"User {user.username} saved in db")
    except Exception:
        logger.exception(f"Failed to save user (tg_id={user_id})")
        logger.info("/start aborted due to persistence failure")
        await state.clear()
        return

    await state.set_state(BotStates.main_menu)
    if is_new:
        intro_text = "Регистрация завершена. Добро пожаловать в бота."
    else:
        intro_text = "Вы уже зарегистрированы в боте."

    await message.answer(
        f"{intro_text} Вот список доступных команд 👇\n\n{AVAILABLE_COMMANDS_TEXT}",
        reply_markup=get_main_menu_kb(),
    )


@router.message(F.text == START_BUTTON_TEXT)
async def cmd_start_text(message: Message, state: FSMContext) -> None:
    await cmd_start(message, state)

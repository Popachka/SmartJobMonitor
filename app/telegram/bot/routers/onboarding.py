from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core.logger import get_app_logger
from app.telegram.bot.keyboards import START_BUTTON_TEXT, get_main_menu_kb
from app.telegram.bot.states import ResumeStates

router = Router()
logger = get_app_logger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else "unknown"
    logger.info(f"Started onboarding for user {user_id}")

    welcome_text = (
        "Привет! 👋\n\n"
        "Я помогу тебе мониторить подходящие вакансии.\n\n"
        "Чтобы начать, загрузи резюме: нажми кнопку «Загрузить резюме».\n"
        "Пока это заглушка, позже добавим обработку резюме."
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_kb())

@router.message(F.text == START_BUTTON_TEXT)
async def cmd_start_text(message: Message, state: FSMContext) -> None:
    await cmd_start(message, state)

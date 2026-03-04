from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from app.domain.shared import LanguageType
from app.telegram.bot.keyboards import HELP_BUTTON_TEXT
from app.telegram.bot.states import BotStates

router = Router()


@router.message(
    StateFilter(BotStates.main_menu, BotStates.processing_resume, None),
    F.text == HELP_BUTTON_TEXT,
)
async def cmd_help(message: Message) -> None:
    available_professions = ", ".join(language.value for language in LanguageType)
    help_text = (
        "❓ Как это работает?\n\n"
        "1. Нажмите «Загрузить новое резюме».\n"
        "2. Отправьте файл в формате PDF.\n"
        "3. Настройте фильтры через «Настроить отслеживание».\n\n"
        f"Сейчас доступны вакансии для профессий: {available_professions}.\n"
        "Если вашей нету, напишите: скоро добавим."
    )
    await message.answer(help_text)

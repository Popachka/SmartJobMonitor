from html import escape

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.domain.shared import LanguageType
from app.telegram.bot.keyboards import HELP_BUTTON_TEXT
from app.telegram.bot.states import BotStates

router = Router()


@router.message(
    StateFilter(BotStates.main_menu, BotStates.processing_resume, None),
    F.text == HELP_BUTTON_TEXT,
)
@router.message(
    StateFilter(BotStates.main_menu, BotStates.processing_resume, None),
    Command("help"),
)
async def cmd_help(message: Message) -> None:
    available_professions = "\n".join(
        f"<b>{escape(language.value)}</b>" for language in LanguageType
    )
    help_text = (
        "❓ Как это работает?\n\n"
        "1. Откройте профиль через /profile или кнопку «Мой профиль».\n"
        "2. Выберите «Заполнить форму (mini-app)», чтобы вручную настроить поиск.\n"
        "3. Или нажмите «Загрузить резюме», чтобы бот сам разобрал профиль из PDF.\n\n"
        "Команда /settings открывает меню ручной настройки.\n\n"
        "Сейчас доступны вакансии для профессий:\n"
        f"{available_professions}\n\n"
    )
    await message.answer(help_text, parse_mode="HTML")

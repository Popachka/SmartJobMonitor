from html import escape

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.domain.shared import SkillType
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
    available_skills = "\n".join(f"<b>{escape(skill.value)}</b>" for skill in SkillType)
    help_text = (
        "Как это работает\n\n"
        "1. Откройте профиль через /profile или кнопку профиля.\n"
        "2. Выберите mini-app форму, чтобы настроить поиск вручную.\n"
        "3. Или загрузите PDF-резюме, чтобы бот сам разобрал профиль.\n\n"
        "Команда /settings открывает меню ручной настройки.\n\n"
        "Сейчас поддерживаются скиллы:\n"
        f"{available_skills}\n"
    )
    await message.answer(help_text, parse_mode="HTML")

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

START_BUTTON_TEXT = "Начать пользоваться ботом"
UPLOAD_BUTTON_TEXT = "📄 Загрузить резюме"
CANCEL_BUTTON_TEXT = "❌ Отмена"
HELP_BUTTON_TEXT = "❓ Помощь"

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=UPLOAD_BUTTON_TEXT)
    builder.button(text=HELP_BUTTON_TEXT)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_start_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=START_BUTTON_TEXT)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=CANCEL_BUTTON_TEXT)
    return builder.as_markup(resize_keyboard=True)

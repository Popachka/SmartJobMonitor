from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

START_BUTTON_TEXT = "Начать пользоваться ботом"
UPLOAD_BUTTON_TEXT = "📄 Загрузить новое резюме"
TRACKING_BUTTON_TEXT = "⚙️ Настроить отслеживание"
CANCEL_BUTTON_TEXT = "❌ Отмена"
HELP_BUTTON_TEXT = "❓ Помощь"

EXPERIENCE_STRICT_TEXT = "Начиная по опыту из резюме"
EXPERIENCE_SOFT_TEXT = "Не учитывать"

SALARY_STRICT_TEXT = "Начиная от зарплаты из резюме"
SALARY_SOFT_TEXT = "Не учитывать"

FORMAT_STRICT_TEXT = "Учитывать формат(Удаленка, Гибрид, Офис) из резюме"
FORMAT_SOFT_TEXT = "Не учитывать"

FORMAT_REMOTE_TEXT = "Удаленка"
FORMAT_HYBRID_TEXT = "Гибрид"
FORMAT_ONSITE_TEXT = "Офис"
FORMAT_ANY_TEXT = "Любой"

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=UPLOAD_BUTTON_TEXT)
    builder.button(text=TRACKING_BUTTON_TEXT)
    builder.button(text=HELP_BUTTON_TEXT)
    builder.adjust(1, 2)
    return builder.as_markup(resize_keyboard=True)


def get_start_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=START_BUTTON_TEXT)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=CANCEL_BUTTON_TEXT)
    return builder.as_markup(resize_keyboard=True)


def get_filter_experience_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=EXPERIENCE_STRICT_TEXT)
    builder.button(text=EXPERIENCE_SOFT_TEXT)
    builder.button(text=CANCEL_BUTTON_TEXT)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_filter_salary_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=SALARY_STRICT_TEXT)
    builder.button(text=SALARY_SOFT_TEXT)
    builder.button(text=CANCEL_BUTTON_TEXT)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_filter_format_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=FORMAT_STRICT_TEXT)
    builder.button(text=FORMAT_SOFT_TEXT)
    builder.button(text=CANCEL_BUTTON_TEXT)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

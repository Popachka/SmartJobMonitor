from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.telegram.bot.keyboards import CANCEL_BUTTON_TEXT, UPLOAD_BUTTON_TEXT, get_main_menu_kb
from app.telegram.bot.states import ResumeStates

router = Router()



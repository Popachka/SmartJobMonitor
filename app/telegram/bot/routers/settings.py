from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.telegram.bot.keyboards import PROFILE_FILL_FORM_CALLBACK, get_start_kb
from app.telegram.bot.settings_menu import send_settings_menu
from app.telegram.bot.states import BotStates

router = Router()


@router.message(
    StateFilter(
        BotStates.main_menu,
        BotStates.waiting_resume,
        BotStates.processing_resume,
        None,
    ),
    Command("settings"),
)
async def cmd_settings(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        await message.answer(
            "Нажмите «Начать пользоваться ботом», чтобы продолжить.",
            reply_markup=get_start_kb(),
        )
        return
    bot = message.bot
    if bot is None:
        return
    await state.set_state(BotStates.main_menu)
    await send_settings_menu(bot, message.chat.id, message.from_user.id)


@router.callback_query(F.data == PROFILE_FILL_FORM_CALLBACK)
async def open_settings_from_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.from_user is None:
        return
    bot = callback.bot
    if bot is None:
        return
    chat_id = callback.from_user.id
    if isinstance(callback.message, Message):
        chat_id = callback.message.chat.id
    await state.set_state(BotStates.main_menu)
    await send_settings_menu(
        bot,
        chat_id,
        callback.from_user.id,
    )

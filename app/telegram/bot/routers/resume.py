from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.telegram.bot.keyboards import (
    CANCEL_BUTTON_TEXT,
    HELP_BUTTON_TEXT,
    TRACKING_BUTTON_TEXT,
    UPLOAD_BUTTON_TEXT,
    get_cancel_kb,
    get_main_menu_kb,
)
from app.telegram.bot.states import BotStates

router = Router()


@router.message(StateFilter(BotStates.main_menu, None), F.text == UPLOAD_BUTTON_TEXT)
async def process_upload_button(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.waiting_resume)
    await message.answer(
        "Отправь резюме в формате PDF.",
        reply_markup=get_cancel_kb(),
    )


@router.message(StateFilter(BotStates.waiting_resume), F.text == CANCEL_BUTTON_TEXT)
async def process_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.main_menu)
    await message.answer(
        "Оставляем как есть.",
        reply_markup=get_main_menu_kb(),
    )


@router.message(StateFilter(BotStates.waiting_resume), F.document)
async def handle_resume_document(message: Message, state: FSMContext) -> None:
    file_name = message.document.file_name or ""
    if not file_name.lower().endswith(".pdf"):
        await message.answer(
            "Поддерживается только PDF. Отправьте PDF файл или нажмите «Отмена».",
            reply_markup=get_cancel_kb(),
        )
        return

    await state.set_state(BotStates.processing_resume)
    processing_message = await message.answer(
        "⏳ Резюме обрабатывается. Это займет немного времени."
    )
    await processing_message.edit_text("✅ Резюме обработалось.")
    await message.answer(
        "✅ Резюме принято. Скоро начнем подбирать вакансии.",
        reply_markup=get_main_menu_kb(),
    )
    await state.set_state(BotStates.main_menu)


@router.message(StateFilter(BotStates.waiting_resume))
async def waiting_resume_fallback(message: Message) -> None:
    await message.answer(
        "Пришлите PDF файл резюме или нажмите «Отмена».",
        reply_markup=get_cancel_kb(),
    )


@router.message(StateFilter(BotStates.processing_resume), F.text == UPLOAD_BUTTON_TEXT)
async def processing_resume_block(message: Message) -> None:
    await message.answer("Ваше резюме уже обрабатывается, подождите.")


@router.message(StateFilter(BotStates.processing_resume), F.document)
async def processing_resume_document_block(message: Message) -> None:
    await message.answer("Ваше резюме уже обрабатывается, подождите.")


@router.message(
    StateFilter(BotStates.main_menu, None),
    ~F.text.in_({UPLOAD_BUTTON_TEXT, TRACKING_BUTTON_TEXT, HELP_BUTTON_TEXT}),
)
async def main_menu_fallback(message: Message) -> None:
    await message.answer(
        "Используйте кнопки меню.",
        reply_markup=get_main_menu_kb(),
    )

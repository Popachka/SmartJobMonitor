from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.application.services.user_service import UserService
from app.domain.shared.value_objects import WorkFormat
from app.domain.user.value_objects import FilterMode
from app.infrastructure.db import UserUnitOfWork, async_session_factory
from app.telegram.bot.keyboards import (
    PROFILE_FILL_FORM_CALLBACK,
    get_main_menu_kb,
    get_settings_menu_kb,
    get_start_kb,
)
from app.telegram.bot.miniapp_payload import (
    SalaryModeChoice,
    WorkFormatChoice,
    parse_miniapp_payload,
)
from app.telegram.bot.states import BotStates
from app.telegram.bot.views.settings import build_settings_menu_text, build_settings_menu_view

router = Router()


async def _send_settings_menu(bot: Bot, chat_id: int, tg_id: int) -> None:
    service = UserService(UserUnitOfWork(async_session_factory))
    user = await service.get_user_by_tg_id(tg_id)
    if user is None:
        await bot.send_message(
            chat_id=chat_id,
            text="Нажмите «Начать пользоваться ботом», чтобы продолжить.",
            reply_markup=get_start_kb(),
        )
        return

    view = build_settings_menu_view(user)
    if not view.specialty_url or not view.format_url or not view.salary_url:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "Mini-app пока не настроен. Обновите `MINI_APP_BASE_URL` "
                "в окружении и попробуйте снова."
            ),
            reply_markup=get_main_menu_kb(),
        )
        return

    await bot.send_message(
        chat_id=chat_id,
        text=build_settings_menu_text(),
        reply_markup=get_settings_menu_kb(
            specialty_and_language_label=view.specialty_label,
            format_label=view.format_label,
            salary_label=view.salary_label,
            specialty_url=view.specialty_url,
            format_url=view.format_url,
            salary_url=view.salary_url,
        ),
    )


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
    await _send_settings_menu(bot, message.chat.id, message.from_user.id)


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
    await _send_settings_menu(
        bot,
        chat_id,
        callback.from_user.id,
    )


@router.message(
    StateFilter(
        BotStates.main_menu,
        BotStates.waiting_resume,
        BotStates.processing_resume,
        None,
    ),
    F.web_app_data,
)
async def handle_web_app_data(message: Message, state: FSMContext) -> None:
    if message.from_user is None or message.web_app_data is None:
        await message.answer(
            "Нажмите «Начать пользоваться ботом», чтобы продолжить.",
            reply_markup=get_start_kb(),
        )
        return

    try:
        payload = parse_miniapp_payload(message.web_app_data.data)
    except ValueError:
        await message.answer("Не удалось сохранить настройки. Проверьте поля формы.")
        return

    if not payload.specializations:
        await message.answer("Выберите минимум одну специализацию.")
        return
    if not payload.primary_languages:
        await message.answer("Выберите минимум один основной язык.")
        return

    if payload.work_format_choice == WorkFormatChoice.ANY:
        work_format = None
        work_format_mode = FilterMode.SOFT
    else:
        work_format = WorkFormat(payload.work_format_choice.value)
        work_format_mode = FilterMode.STRICT

    if payload.salary_mode == SalaryModeChoice.FROM:
        salary_mode = FilterMode.STRICT
        salary_amount_rub = payload.salary_amount_rub
    else:
        salary_mode = FilterMode.SOFT
        salary_amount_rub = None

    service = UserService(UserUnitOfWork(async_session_factory))
    updated = await service.update_profile_from_miniapp(
        tg_id=message.from_user.id,
        specializations=[item.value for item in payload.specializations],
        primary_languages=[item.value for item in payload.primary_languages],
        work_format=work_format,
        work_format_mode=work_format_mode,
        salary_amount_rub=salary_amount_rub,
        salary_mode=salary_mode,
    )
    if not updated:
        await message.answer(
            "Нажмите «Начать пользоваться ботом», чтобы продолжить.",
            reply_markup=get_start_kb(),
        )
        return

    await state.set_state(BotStates.main_menu)
    await message.answer("Профиль обновлен.")
    bot = message.bot
    if bot is None:
        return
    await _send_settings_menu(bot, message.chat.id, message.from_user.id)

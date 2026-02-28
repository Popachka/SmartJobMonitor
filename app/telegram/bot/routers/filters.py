from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.application.services.user_service import UserService
from app.domain.user.value_objects import FilterMode, WorkFormat
from app.infrastructure.db import UserUnitOfWork, async_session_factory
from app.telegram.bot.keyboards import (
    CANCEL_BUTTON_TEXT,
    EXPERIENCE_SOFT_TEXT,
    EXPERIENCE_STRICT_TEXT,
    FORMAT_ANY_TEXT,
    FORMAT_HYBRID_TEXT,
    FORMAT_ONSITE_TEXT,
    FORMAT_REMOTE_TEXT,
    SALARY_SOFT_TEXT,
    SALARY_STRICT_TEXT,
    TRACKING_BUTTON_TEXT,
    get_filter_experience_kb,
    get_filter_format_kb,
    get_filter_salary_kb,
    get_main_menu_kb,
    get_start_kb,
)
from app.telegram.bot.states import BotStates

router = Router()

EXP_MODE_KEY = "exp_mode"
SALARY_MODE_KEY = "salary_mode"
FORMAT_KEY = "format_choice"


@router.message(
    StateFilter(BotStates.main_menu, BotStates.processing_resume),
    F.text == TRACKING_BUTTON_TEXT,
)
async def start_filter_wizard(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BotStates.filter_experience)
    await message.answer(
        "Настроим фильтры. Как учитывать опыт?",
        reply_markup=get_filter_experience_kb(),
    )


@router.message(
    StateFilter(BotStates.filter_experience),
    F.text.in_({EXPERIENCE_STRICT_TEXT, EXPERIENCE_SOFT_TEXT}),
)
async def filter_experience_step(message: Message, state: FSMContext) -> None:
    mode = (
        FilterMode.STRICT
        if message.text == EXPERIENCE_STRICT_TEXT
        else FilterMode.SOFT
    )
    await state.update_data({EXP_MODE_KEY: mode.value})
    await state.set_state(BotStates.filter_salary)
    await message.answer(
        "Как учитывать зарплату?",
        reply_markup=get_filter_salary_kb(),
    )


@router.message(
    StateFilter(BotStates.filter_salary),
    F.text.in_({SALARY_STRICT_TEXT, SALARY_SOFT_TEXT}),
)
async def filter_salary_step(message: Message, state: FSMContext) -> None:
    mode = (
        FilterMode.STRICT
        if message.text == SALARY_STRICT_TEXT
        else FilterMode.SOFT
    )
    await state.update_data({SALARY_MODE_KEY: mode.value})
    await state.set_state(BotStates.filter_format)
    await message.answer(
        "Выберите формат работы:",
        reply_markup=get_filter_format_kb(),
    )


@router.message(
    StateFilter(BotStates.filter_format),
    F.text.in_(
        {FORMAT_REMOTE_TEXT, FORMAT_HYBRID_TEXT, FORMAT_ONSITE_TEXT, FORMAT_ANY_TEXT}
    ),
)
async def filter_format_step(message: Message, state: FSMContext) -> None:
    await state.update_data({FORMAT_KEY: message.text})
    data = await state.get_data()

    exp_mode = FilterMode(data.get(EXP_MODE_KEY, FilterMode.SOFT.value))
    salary_mode = FilterMode(data.get(SALARY_MODE_KEY, FilterMode.SOFT.value))

    format_choice = data.get(FORMAT_KEY)
    if format_choice == FORMAT_REMOTE_TEXT:
        work_format = WorkFormat.REMOTE
        work_format_mode = FilterMode.STRICT
    elif format_choice == FORMAT_HYBRID_TEXT:
        work_format = WorkFormat.HYBRID
        work_format_mode = FilterMode.STRICT
    elif format_choice == FORMAT_ONSITE_TEXT:
        work_format = WorkFormat.ONSITE
        work_format_mode = FilterMode.STRICT
    else:
        work_format = None
        work_format_mode = FilterMode.SOFT

    service = UserService(UserUnitOfWork(async_session_factory))
    updated = await service.update_filters(
        tg_id=message.from_user.id,
        experience_mode=exp_mode,
        salary_mode=salary_mode,
        work_format=work_format,
        work_format_mode=work_format_mode,
    )
    if not updated:
        await state.clear()
        await message.answer(
            "Нажмите «Начать пользоваться ботом», чтобы продолжить.",
            reply_markup=get_start_kb(),
        )
        return

    await state.clear()
    await state.set_state(BotStates.main_menu)
    await message.answer(
        "Фильтры обновлены.",
        reply_markup=get_main_menu_kb(),
    )


@router.message(
    StateFilter(
        BotStates.filter_experience,
        BotStates.filter_salary,
        BotStates.filter_format,
    ),
    F.text == CANCEL_BUTTON_TEXT,
)
async def cancel_filter_wizard(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BotStates.main_menu)
    await message.answer(
        "Настройка отменена.",
        reply_markup=get_main_menu_kb(),
    )

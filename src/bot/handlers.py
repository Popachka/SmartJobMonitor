from io import BytesIO

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.infrastructure.db import async_session
from src.infrastructure.exceptions import TooManyPagesError, NotAResumeError
from src.infrastructure.logger import get_app_logger
from src.infrastructure.parsers import ParserFactory
from src.repositories.user_repository import UserRepository
from src.services.resume_service import ResumeService

router = Router()
logger = get_app_logger(__name__)


class ResumeStates(StatesGroup):
    main_menu = State()
    waiting_resume = State()
    processing_resume = State()


START_BUTTON_TEXT = "Начать пользоваться ботом"
UPLOAD_BUTTON_TEXT = "📄 Загрузить резюме"
CANCEL_BUTTON_TEXT = "❌ Отмена"


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=UPLOAD_BUTTON_TEXT)
    builder.button(text="❓ Помощь")
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

class IsUnregistered(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        async with async_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_tg_id(tg_id=message.from_user.id)
        return user is None


@router.message(StateFilter(None), ~Command("start"), ~F.text == START_BUTTON_TEXT, IsUnregistered())
async def require_start(message: types.Message):
    await message.answer(
        "Вы ещё не зарегистрированы. Нажмите «Начать пользоваться ботом» (/start).",
        reply_markup=get_start_kb(),
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    async with async_session() as session:
        repo = UserRepository(session)
        user = await repo.get_or_create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username,
        )

    welcome_text = (
        f"Привет, {user.username or 'друг'}! 👋\n\n"
        "Я помогу тебе мониторить подходящие вакансии.\n\n"
        "Чтобы начать, загрузи резюме: нажми кнопку «Загрузить резюме» и отправь файл.\n\n"
        "**Правила:**\n"
        "1️⃣ Принимаю только **PDF**.\n"
        "2️⃣ Максимум **10 страниц**.\n"
        "3️⃣ Анализ занимает от 20 до 150 секунд."
    )
    await state.set_state(ResumeStates.main_menu)
    await message.answer(welcome_text, reply_markup=get_main_menu_kb(), parse_mode="Markdown")


@router.message(F.text == START_BUTTON_TEXT)
async def cmd_start_text(message: types.Message, state: FSMContext):
    await cmd_start(message, state)


@router.message(StateFilter(ResumeStates.main_menu, ResumeStates.processing_resume, None), F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    help_text = (
        "❓ **Как это работает?**\n\n"
        "1. Нажмите кнопку 'Загрузить резюме'.\n"
        "2. Отправьте файл вашего резюме.\n"
        "3. Бот извлечёт ваш стек технологий и сохранит его.\n"
        "4. На основе этих данных будут подбираться вакансии."
    )
    await message.answer(help_text, parse_mode="Markdown")


@router.message(StateFilter(ResumeStates.main_menu, None), F.text == UPLOAD_BUTTON_TEXT)
async def process_upload_button(message: types.Message, state: FSMContext):
    await state.set_state(ResumeStates.waiting_resume)
    await message.answer(
        "Отправь мне своё резюме в формате **PDF** 📄",
        reply_markup=get_cancel_kb(),
        parse_mode="Markdown",
    )


@router.message(StateFilter(ResumeStates.main_menu, None))
async def main_menu_fallback(message: types.Message):
    await message.answer(
        "Чтобы загрузить резюме, нажмите «Загрузить резюме», затем отправьте PDF файл.",
        reply_markup=get_main_menu_kb(),
    )


@router.message(ResumeStates.waiting_resume, F.text == CANCEL_BUTTON_TEXT)
async def process_cancel(message: types.Message, state: FSMContext):
    await state.set_state(ResumeStates.main_menu)
    await message.answer("Загрузка отменена. Возвращаемся в меню.", reply_markup=get_main_menu_kb())


@router.message(ResumeStates.waiting_resume, F.document)
async def handle_resume_document(message: types.Message, state: FSMContext):
    if message.document.file_size > 15 * 1024 * 1024:
        return await message.answer("Файл слишком большой. Максимум 15 МБ.")

    await state.set_state(ResumeStates.processing_resume)

    async def reset_to_menu(err_msg: str):
        await message.answer(f"⚠️ {err_msg}", reply_markup=get_main_menu_kb())
        await state.set_state(ResumeStates.main_menu)

    try:
        parser = ParserFactory.get_parser_by_extension(message.document.file_name)
    except ValueError:
        return await reset_to_menu("Формат не поддерживается.")

    processing_msg = await message.answer(
        "⏳ Резюме обрабатывается. Это может занять до пары минут."
    )
    await message.answer(
        "После анализа резюме вам начнут предлагаться подходящие вакансии по простым критериям:\n"
        "1) Опыт — стаж близок к требованию вакансии.\n"
        "2) Специализация (Backend, Frontend, Fullstack и т.д.).\n"
        "3) Язык (Python, Java, C# и т.д.).\n"
        "Даже если в резюме несколько языков и специализаций, бот это учтёт.",
        reply_markup=get_main_menu_kb(),
    )
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    buffer = BytesIO()
    try:
        await message.bot.download(message.document.file_id, destination=buffer)

        async with async_session() as session:
            service = ResumeService(session=session)
            await service.process_resume(source=buffer, parser=parser, tg_id=message.from_user.id)

        current_state = await state.get_state()
        if current_state != ResumeStates.processing_resume:
            return

        try:
            await processing_msg.edit_text("✅ Резюме обработалось.")
        except Exception:
            await message.answer("✅ Резюме обработалось.")
        await message.answer("Бот уже начал отслеживать для вас подходящие вакансии.")
        await state.set_state(ResumeStates.main_menu)

    except NotAResumeError:
        await reset_to_menu("Этот файл не похож на резюме.")
    except TooManyPagesError:
        await reset_to_menu("Слишком много страниц (макс. 10).")
    except Exception:
        logger.exception("ResumeService failed")
        await reset_to_menu("Произошла ошибка при анализе.")
    finally:
        buffer.close()


@router.message(ResumeStates.waiting_resume)
async def waiting_resume_fallback(message: types.Message):
    await message.answer(
        "Если хотите загрузить резюме, отправьте PDF файл. "
        "Или нажмите «Отмена», чтобы выйти в меню.",
        reply_markup=get_cancel_kb(),
    )


@router.message(ResumeStates.processing_resume, F.text == UPLOAD_BUTTON_TEXT)
async def processing_resume_block(message: types.Message):
    await message.answer("Ваше резюме уже обрабатывается, подождите.")


@router.message(ResumeStates.processing_resume, ~F.text.in_({UPLOAD_BUTTON_TEXT, "❓ Помощь"}))
async def processing_resume_ignore(message: types.Message):
    await message.answer("Меню доступно ниже", reply_markup=get_main_menu_kb())

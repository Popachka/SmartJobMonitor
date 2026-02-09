from io import BytesIO
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from src.infrastructure.db import async_session
from src.infrastructure.logger import get_app_logger
from src.repositories.user_repository import UserRepository
from src.services.resume_service import ResumeService
from src.infrastructure.parsers import ParserFactory
from src.infrastructure.exceptions import ParserError, TooManyPagesError, NotAResumeError

router = Router()
logger = get_app_logger(__name__)

# --- States ---

class ResumeStates(StatesGroup):
    main_menu = State()       # Главное меню
    waiting_resume = State()  # Ожидание файла PDF

# --- Keyboards ---

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📄 Загрузить новое резюме")
    builder.button(text="❓ Помощь")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)

# --- Handlers ---

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
        "**Правила:**\n"
        "1️⃣ Принимаю только **PDF**.\n"
        "2️⃣ Максимум **10 страниц**.\n"
        "3️⃣ Анализ занимает от 20 до 150 секунд."
    )
    await state.set_state(ResumeStates.main_menu)
    await message.answer(welcome_text, reply_markup=get_main_menu_kb(), parse_mode="Markdown")

# Кнопки работают в main_menu или если состояние сброшено (None)
@router.message(StateFilter(ResumeStates.main_menu, None), F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    help_text = (
        "❓ **Как это работает?**\n\n"
        "1. Нажмите кнопку 'Загрузить новое резюме'.\n"
        "2. Отправьте файл вашего резюме.\n"
        "3. Бот извлечет ваш стек технологий и сохранит его.\n"
        "4. На основе этих данных будут подбираться вакансии."
    )
    await message.answer(help_text, parse_mode="Markdown")

@router.message(StateFilter(ResumeStates.main_menu, None), F.text == "📄 Загрузить новое резюме")
async def process_upload_button(message: types.Message, state: FSMContext):
    await state.set_state(ResumeStates.waiting_resume)
    await message.answer(
        "Отправь мне свое резюме в формате **PDF** 📄",
        reply_markup=get_cancel_kb(),
        parse_mode="Markdown"
    )

@router.message(ResumeStates.waiting_resume, F.text == "❌ Отмена")
async def process_cancel(message: types.Message, state: FSMContext):
    await state.set_state(ResumeStates.main_menu)
    await message.answer("Загрузка отменена. Возвращаемся в меню.", reply_markup=get_main_menu_kb())

@router.message(ResumeStates.waiting_resume, F.document)
async def handle_resume_document(message: types.Message, state: FSMContext):
    async def reset_to_menu(err_msg: str):
        await message.answer(
            f"⚠️ {err_msg}\n\nПожалуйста, нажмите кнопку заново.",
            reply_markup=get_main_menu_kb()
        )
        await state.set_state(ResumeStates.main_menu)

    # Проверка на PDF
    if not message.document.file_name.lower().endswith('.pdf'):
        return await reset_to_menu("Бот поддерживает только PDF.")

    try:
        parser = ParserFactory.get_parser_by_extension(message.document.file_name)
    except ValueError:
        return await reset_to_menu("Формат не поддерживается.")

    processing_msg = await message.answer("⏳ Принял! Начинаю обработку (обычно это занимает 20-60 сек)...")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    buffer = BytesIO()
    try:
        await message.bot.download(message.document.file_id, destination=buffer)
    except Exception as exc:
        logger.error(f"Download error: {exc}")
        buffer.close()
        return await reset_to_menu("Ошибка при загрузке файла.")

    async with async_session() as session:
        service = ResumeService(session=session)
        try:
            await service.process_resume(source=buffer, parser=parser, tg_id=message.from_user.id)
            
            # Проверка: не нажал ли пользователь "Отмена", пока шел парсинг
            if await state.get_state() != ResumeStates.waiting_resume:
                return

            await processing_msg.edit_text("✅ Успешно! Резюме проанализировано.")
            await message.answer("Теперь я буду искать вакансии для тебя.", reply_markup=get_main_menu_kb())
            await state.set_state(ResumeStates.main_menu)

        except NotAResumeError:
            await reset_to_menu("Этот файл не похож на резюме.")
        except TooManyPagesError:
            await reset_to_menu("Слишком много страниц (макс. 10).")
        except (ParserError, Exception):
            logger.exception("ResumeService failed")
            await reset_to_menu("Произошла ошибка при анализе.")
        finally:
            buffer.close()
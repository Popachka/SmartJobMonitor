from io import BytesIO

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.infrastructure.db import async_session
from src.infrastructure.logger import get_app_logger
from src.repositories.user_repository import UserRepository
from src.services.resume_service import ResumeService
from src.infrastructure.parsers import ParserFactory
from src.infrastructure.exceptions import ParserError, TooManyPagesError, NotAResumeError
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()
logger = get_app_logger(__name__)


class ResumeStates(StatesGroup):
    main_menu = State()       # Пользователь в главном меню
    waiting_resume = State()  # Ожидание файла после нажатия кнопки


def get_main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Загрузить новое резюме")
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    async with async_session() as session:
        repo = UserRepository(session)
        user = await repo.get_or_create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username,
        )

    # Правила и приветствие
    welcome_text = (
        f"Привет, {user.username or 'друг'}!\n\n"
        "**Правила бота:**\n"
        "1. Бот принимает резюме только в формате PDF.\n"
        "2. Объем не должен превышать 10 страниц.\n"
        "3. После анализа я начну подбирать подходящие вакансии."
    )

    await state.set_state(ResumeStates.main_menu)
    await message.answer(welcome_text, reply_markup=get_main_menu_kb())

@router.message(ResumeStates.main_menu, F.text == "Загрузить новое резюме")
async def process_upload_button(message: types.Message, state: FSMContext):
    await state.set_state(ResumeStates.waiting_resume)
    await message.answer("Отправь мне свое резюме в PDF формате.")


@router.message(ResumeStates.waiting_resume, F.document)
async def handle_resume_document(message: types.Message, state: FSMContext):
    async def reset_to_menu(err_msg: str):
        await message.answer(f"{err_msg}\n\nПожалуйста, нажмите кнопку «Загрузить новое резюме» еще раз.")
        await state.set_state(ResumeStates.main_menu)

    try:
        parser = ParserFactory.get_parser_by_extension(
            message.document.file_name)
    except ValueError:
        return await reset_to_menu('Формат не поддерживается.')

    await message.answer("Принял! Проверяю резюме...")

    try:
        buffer = BytesIO()
        await message.bot.download(message.document.file_id, destination=buffer)
    except Exception as exc:
        logger.error(f"Ошибка загрузки: {exc}")
        return await reset_to_menu("Не удалось скачать файл.")

    async with async_session() as session:
        service = ResumeService(session=session)
        try:
            data = await service.process_resume(source=buffer, parser=parser)
            await message.answer(
                f"Успешно! Ваш стек: {', '.join(data.tech_stack)}",
                reply_markup=get_main_menu_kb()
            )
            await state.set_state(ResumeStates.main_menu) 

        except NotAResumeError:
            await reset_to_menu("Этот файл не похож на резюме.")
        except TooManyPagesError:
            await reset_to_menu("Файл слишком большой (макс. 10 страниц).")
        except (ParserError, Exception) as e:
            logger.exception("Ошибка при обработке")
            await reset_to_menu("Произошла техническая ошибка на сервере.")


@router.message(ResumeStates.waiting_resume)
async def handle_other_message_waiting(message: types.Message):
    await message.answer("Я жду именно PDF файл. Если передумали, нажмите кнопку или отправьте файл.")

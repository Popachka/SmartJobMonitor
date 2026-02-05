from aiogram import Router, types
from aiogram.filters import Command
from src.core.db import async_session
from src.services.user_service import UserService
from src.workers.tasks import parse_resume_task

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    async with async_session() as session:
        service = UserService(session)
        user = await service.get_or_create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username
        )
    await message.answer(
        f"Привет {user.username}! Я бот для мониторинга вакансий.\n"
        "Пришли мне текст своего резюме, и я начну подбирать подходящие позиции."
    )

@router.message()
async def handle_resume(message: types.Message):
    if not message.text:
        return

    await message.answer("Принял! Начинаю анализировать ваше резюме...")
    
    # Отправляем задачу в Taskiq
    await parse_resume_task.kiq(
        tg_id=message.from_user.id,
        text=message.text
    )
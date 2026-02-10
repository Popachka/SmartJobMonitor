from aiogram import Bot, Dispatcher
from src.bot.handlers import router
from src.infrastructure.logger import get_app_logger

logger = get_app_logger(__name__)
async def start_bot(bot: Bot):
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("Бот запущен...")
    await dp.start_polling(bot)
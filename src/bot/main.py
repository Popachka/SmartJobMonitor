from aiogram import Bot, Dispatcher
from src.core.config import config
from src.bot.handlers import router
from src.core.logger import get_app_logger

logger = get_app_logger(__name__)
async def start_bot():
    bot = Bot(token=config.BOT_TOKEN) 
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("Бот запущен...")
    await dp.start_polling(bot)
import asyncio
from src.infrastructure.logger import get_app_logger
from src.bot.scrapper import TelegramScraper
from src.infrastructure.db import async_session 
from src.bot.main import start_bot
from aiogram import Bot
from src.infrastructure.config import config

logger = get_app_logger(__name__)

async def main():
    bot = Bot(token=config.BOT_TOKEN)

    scraper = TelegramScraper(
        session_factory=async_session,
        bot=bot,
    )

    try:
        await asyncio.gather(
            scraper.start(),
            start_bot(bot),
        )
    finally:
        await bot.session.close()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Работа завершена.")
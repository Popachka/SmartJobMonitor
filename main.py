import asyncio
from src.core.logger import get_app_logger
from src.scrapper import TelegramScraper
from src.core.db import async_session 
logger = get_app_logger(__name__)

async def main():
    scraper = TelegramScraper(session_factory=async_session)
    
    try:
        await scraper.start()
    except Exception as e:
        logger.critical(f"Ошибка при работе приложения: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Работа завершена.")
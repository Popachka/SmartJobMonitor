import asyncio
from src.infrastructure.logger import get_app_logger
from src.infrastructure.metrics import MetricsService
from src.infrastructure.sentry import init_sentry
from src.bot.scrapper import TelegramScraper
from src.infrastructure.db import async_session 
from src.bot.main import start_bot
from aiogram import Bot
from src.infrastructure.config import config

logger = get_app_logger(__name__)

async def main():
    init_sentry()

    metrics_service = MetricsService(
        enabled=config.METRICS_ENABLED,
        addr=config.METRICS_ADDR,
        port=config.METRICS_PORT,
    )
    metrics_service.start()

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
        await metrics_service.stop()
        await bot.session.close()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Работа завершена.")

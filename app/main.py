import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.infrastructure.db import async_session_factory
from app.infrastructure.llm_provider import GoogleLLMExtractor
from app.infrastructure.sentry import init_sentry
from app.infrastructure.telegram.telethon_client import TelethonClientProvider
from app.telegram.bot import get_router as get_bot_router
from app.telegram.scrapper.handlers import TelegramScraper


async def build_scraper() -> tuple[TelegramScraper, TelethonClientProvider]:
    provider = TelethonClientProvider()
    client = await provider.start()
    extractor = GoogleLLMExtractor()
    return TelegramScraper(client, async_session_factory, extractor), provider


def build_bot() -> tuple[Dispatcher, Bot]:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(get_bot_router())
    return dp, bot


async def main() -> None:
    init_sentry()
    scraper, provider = await build_scraper()
    dp, bot = build_bot()
    try:
        scraper_task = asyncio.create_task(scraper.start())
        bot_task = asyncio.create_task(dp.start_polling(bot))
        await asyncio.gather(scraper_task, bot_task)
    finally:
        await provider.stop()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

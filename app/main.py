import asyncio

from app.infrastructure.db import async_session_factory
from app.infrastructure.llm_provider import GoogleLLMExtractor
from app.infrastructure.sentry import init_sentry
from app.infrastructure.telegram.telethon_client import TelethonClientProvider
from app.telegram.scrapper.handlers import TelegramScraper


async def build_scraper() -> tuple[TelegramScraper, TelethonClientProvider]:
    provider = TelethonClientProvider()
    client = await provider.start()
    extractor = GoogleLLMExtractor()
    return TelegramScraper(client, async_session_factory, extractor), provider


async def main() -> None:
    init_sentry()
    scraper, provider = await build_scraper()
    try:
        await scraper.start()
    finally:
        await provider.stop()


if __name__ == "__main__":
    asyncio.run(main())

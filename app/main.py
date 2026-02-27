import asyncio

from app.infrastructure.telegram.telethon_client import TelethonClientProvider
from app.telegram.scrapper.handlers import TelegramScraper


async def build_scraper() -> tuple[TelegramScraper, TelethonClientProvider]:
    provider = TelethonClientProvider()
    client = await provider.start()
    return TelegramScraper(client), provider


async def main() -> None:
    scraper, provider = await build_scraper()
    try:
        await scraper.start()
    finally:
        await provider.stop()


if __name__ == "__main__":
    asyncio.run(main())

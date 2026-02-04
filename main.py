import asyncio
from src.scrapper import start_scrapper
from src.core.logger import get_app_logger

logger = get_app_logger(__name__)


async def main():
    await start_scrapper()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

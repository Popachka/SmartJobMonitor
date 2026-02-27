from telethon import TelegramClient, events

from app.core.config import config
from app.core.logger import get_app_logger
from app.telegram.scrapper.channels import normalized_channels

logger = get_app_logger(__name__)


class TelegramScraper:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def _message_handler(self, event: events.NewMessage.Event) -> None:
        pass

    async def start(self) -> None:
        channels = normalized_channels(config.CHANNELS)
        logger.info("Scraper listens channels: %s", channels)
        self.client.add_event_handler(
            self._message_handler,
            events.NewMessage(chats=channels),
        )
        logger.info("Scraper started.")
        await self.client.run_until_disconnected()

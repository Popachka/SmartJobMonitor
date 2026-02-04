from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
from src.core.config import config
from src.core.logger import get_app_logger

logger = get_app_logger(__name__)

client = TelegramClient('first_session', config.API_ID, config.API_HASH)

@client.on(events.NewMessage(chats=config.CHANNELS))
async def handler(event: events.NewMessage.Event):
    sender = await event.get_sender()

    msg: Message = event.message
    text = msg.text
    
    logger.info(f"Новое сообщение от {getattr(sender, 'username', 'Unknown')}")
    logger.debug(f"Полный текст: {text}")
    
async def start_scrapper():
    await client.start()
    logger.info("Scraper запущен и ожидает сообщений...")
    
    await client.run_until_disconnected()
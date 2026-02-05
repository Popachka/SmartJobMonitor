from telethon import TelegramClient, events
from src.core.config import config
from src.core.logger import get_app_logger
from telethon.tl.types import Message
from src.services.vacancy_service import VacancyService
from src.workers.tasks import parse_vacancy_task
logger = get_app_logger(__name__)

class TelegramScraper:
    def __init__(self, session_factory):
        self.client = TelegramClient('first_session', config.API_ID, config.API_HASH)
        self.session_factory = session_factory
    async def _message_handler(self, event: events.NewMessage.Event):
        logger.debug(f"Event: {event}")
        async with self.session_factory() as session:
            service = VacancyService(session)
            try:
                raw_vancancy = await service.create_raw_vacancy(
                    text=event.message.text,
                    chat_id=event.chat_id,
                    message_id=event.message.id
                )
                logger.info(f"Вакансия {raw_vancancy.id} успешно сохранена через Service")
                
                await parse_vacancy_task.kiq(raw_vancancy.id)
                logger.debug(f"Задача на парсинг вакансии {raw_vancancy.id} отправлена в очередь")
                
            except Exception as e:
                logger.error(f"Ошибка в обработчике скрапера: {e}")
    async def start(self):
        self.client.add_event_handler(
            self._message_handler,
            events.NewMessage(chats=config.CHANNELS)
        )
        await self.client.start()
        logger.info("Scraper запущен и ожидает сообщений...")
        await self.client.run_until_disconnected()
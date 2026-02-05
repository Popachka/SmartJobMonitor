from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
from src.core.config import config
from src.core.logger import get_app_logger

from src.core.db import async_session
from src.models.vacancy import RawVacancy

logger = get_app_logger(__name__)

client = TelegramClient('first_session', config.API_ID, config.API_HASH)

# какая информация есть у паста? Можно ли его затем пересылать?
@client.on(events.NewMessage(chats=config.CHANNELS))
async def handler(event: events.NewMessage.Event):
    msg: Message = event.message
    logger.debug(f'Message: {msg}')

    chat = await event.get_chat()
    logger.debug(f"Chat: {chat}")

    source_username = getattr(chat, 'username', 'Unknown')
    chat_id = event.chat_id
    message_id = msg.id
    text = msg.text
    logger.info(f"Новое сообщение из {source_username} (ID: {message_id})")
    async with async_session() as session:
        try:
            raw = RawVacancy(
                source = source_username,
                raw_text = text,
                chat_id = chat_id,
                message_id = message_id,
                status = 0
            )
            session.add(raw)
            await session.commit()
            logger.info(f"Запись {raw.id} сохранена в БД")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при сохранении в БД: {e}")

        # forwarded = await client.forward_messages(
        #     entity='me',
        #     messages=message_id,
        #     from_peer=chat_id
        # )

        # target_msg = forwarded
        
        # if target_msg:
        #     await target_msg.reply(
        #         f"🤖 Вакансия записана в базу!\n"
        #         f"ID в БД: {raw.id}\n"
        #         f"Статус: Ожидает парсинга"
        #     )

        # logger.info("Сообщение успешно переслано в Избранное с ответом")
async def start_scrapper():
    await client.start()
    logger.info("Scraper запущен и ожидает сообщений...")
    
    await client.run_until_disconnected()


#     # Пример логики пересылки
# await client.forward_messages(
#     entity=user_id,          # Кому отправляем
#     messages=saved_message_id, # ID сообщения из базы
#     from_peer=saved_chat_id    # ID канала из базы
# )
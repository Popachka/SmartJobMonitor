from aiogram import Bot
from aiogram.types import BotCommand


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Перезапустить и открыть меню"),
            BotCommand(command="profile", description="Показать профиль поиска"),
            BotCommand(command="settings", description="Открыть настройки ленты"),
            BotCommand(command="help", description="Как это работает"),
        ]
    )

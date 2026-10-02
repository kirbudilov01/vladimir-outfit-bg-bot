import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from .bot import register_handlers
from .config import get_settings
from .db import Store
from .processor import BackgroundComposer


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    store = Store(settings.database_path)
    composer = BackgroundComposer(settings)
    await register_handlers(dp, bot, store, composer, settings)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="status", description="Статус"),
            BotCommand(command="set_background", description="Задать фон"),
            BotCommand(command="cancel", description="Отмена"),
            BotCommand(command="help", description="Помощь"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

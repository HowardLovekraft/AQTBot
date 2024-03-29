import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n

i18n = I18n(path="locales", default_locale="en", domain="messages")

import database.aqt_db as aqt_db
from handlers import commands, questionthread
from env.env_reader import get_token


async def main():
    await aqt_db.db_connect()

    print('DB  --> WORKS')
    bot = Bot(token=get_token())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(commands.router,
                       questionthread.router)

    print('BOT --> WORKS')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot,
                           allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot was stopped by Ctrl-C")

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from env.env_reader import EnvVars
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

env_vars = EnvVars()
i18n = I18n(path="locales", default_locale="ru", domain="messages")
i18n_middleware = SimpleI18nMiddleware(i18n)

from handlers import commands, questionthread
import AQT.database.postgre_db as aqt_db


async def main():
    await aqt_db.db_connect()
    print('DB  --> WORKS')

    bot = Bot(token=env_vars.token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(commands.router,
                       questionthread.router)

    print('BOT --> WORKS')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot was stopped by Ctrl-C")

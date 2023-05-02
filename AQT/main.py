import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import commands, questionthread

import AQT.database.aqt_db as aqt_db

async def main():

    await aqt_db.db_connect()
    print('DB  --> WORKS')

    load_dotenv(dotenv_path="venv.env")
    TOKEN_API = getenv('TOKEN_API')
    bot = Bot(token=TOKEN_API)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(commands.router,
                       questionthread.router)

    print('BOT --> WORKS')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


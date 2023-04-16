import asyncio
import string
import secrets
import sqlite3 as sq
from aiogram.types import ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


from aqt_keyboards import *
from config import TOKEN_API
from msgs import *
import aqt_db

storage = MemoryStorage()
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot,
                storage=storage)


class ThreadOwnerStatesGroup(StatesGroup):
    question = State()
    answer = State()

class AskerStatesGroup(StatesGroup):
    number = State()
    question = State()


async def db_connect() -> None:
    global db, cur
    db = sq.connect('aqt.db')
    cur = db.cursor()

async def generate_random_code():
    letters = string.ascii_uppercase
    return ''.join(secrets.choice(letters) for i in range(6))

async def generator():
    return await generate_random_code()


async def on_startup(_):
    await aqt_db.db_connect()
    print('DB  --> WORKS')
    print('BOT --> WORKS')


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(text=PRE_START_MSG,
                         reply_markup=get_accept_ikb())


@dp.message_handler(commands=['cancel'], state= '*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply('U canceled the process', reply_markup=get_start_kb())



@dp.message_handler(Text("Create a new thread"))
async def create_aqt(message: types.Message):
    THREAD_ID = await generator()
    await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    await message.answer(text=f"Okay, ur thread's ID is {THREAD_ID}\nSend ur ID to ur friends and get anonymous questions!")


@dp.message_handler(Text("Write into exist thread"))
async def work_aqt(message: types.Message):
    await message.answer(text=WHEN_WORK_MSG,
                         reply_markup=get_cancel_kb())
    await AskerStatesGroup.number.set()


@dp.message_handler(state=AskerStatesGroup.number)
async def check_and_load_id(message: types.Message, state: FSMContext) -> None:
    if await aqt_db.check_thread_id(message.text):
        async with state.proxy() as data:
            data['thread_id'] = message.text
        await message.reply("Okay, write a question ^-^")
        await AskerStatesGroup.next()
    else:
        await message.reply("This code doesn'e exist in DB. Type valid code")

@dp.message_handler(state=AskerStatesGroup.question)
async def load_question(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['question'] = message.text
    user_id = await aqt_db.get_interviewee_id(data['thread_id'])
    #interviewer_id = await aqt_db.set_interviewer()
    await bot.send_message(chat_id=user_id[0],
                           text=f"U got a question from {data['thread_id']}'s thread\n\n{data['question']}\n\nTo answer on question, reply this message and write an answer")

    await message.reply(f"Okay, I sent ur message to {data['thread_id']} thread.", # If u need to delete it, push on reaction.",
                        reply_markup=get_start_kb())
                                                                                   # don't forget about replying and deleting
    await state.finish()

# @dp.message_handler(state=ThreadOwnerStatesGroup.answer)
# async def get_answer(message: types.Message, state: FSMContext) -> None:
#     async with state.proxy() as data:
#         data['answer'] = message.text
#     await message.reply("U got an answer from {THREAD_ID}\n\n{ANSWER_TEXT}")
#     await state.finish()


@dp.callback_query_handler()
async def log_accept_handler(callback: types.CallbackQuery):
    if callback.data == "accept":
        await callback.message.delete()
        await callback.answer()
        await callback.message.answer(text=START_MSG,
                        reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.delete()
        await callback.answer()
        await callback.message.answer(text=NO_LOG_MSG)

@dp.errors_handler(exception=BotBlocked)
async def bot_was_blocked(update: types.Update, exception=BotBlocked) -> bool:
    print("NOTICE - Can't send message because I was blocked")
    return True


if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
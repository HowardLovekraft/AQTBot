import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

import aqt_db
from keyboards import *
from messages import *
from code_generator import generator


load_dotenv(dotenv_path="venv.env")

TOKEN_API = os.getenv('TOKEN_API')
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
    sent_question = State()


async def on_startup(_):
    await aqt_db.db_connect()
    print('DB  --> WORKS')
    print('BOT --> WORKS')


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(text=ACCEPT_LOGS_MSG,
                         reply_markup=get_accept_ikb())


@dp.message_handler(commands=['cancel'], state= '*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply(CANCEL_MSG, reply_markup=get_start_kb())



@dp.message_handler(Text("Create a new thread"))
async def create_aqt(message: types.Message):
    THREAD_ID = await generator()
    await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    await message.answer(text=f"Okay, ur thread's ID is {THREAD_ID}"
                              f"{CREATE_THREAD_MSG}")


@dp.message_handler(Text("Write into exist thread"))
async def work_aqt(message: types.Message):
    await message.answer(text=WAIT_CODE_MSG,
                         reply_markup=get_cancel_kb())
    await AskerStatesGroup.number.set()


@dp.message_handler(state=AskerStatesGroup.number)
async def check_and_load_id(message: types.Message, state: FSMContext) -> None:
    if await aqt_db.check_thread_id(message.text):
        async with state.proxy() as data:
            data['thread_id'] = message.text
        await message.reply(WAIT_QUESTION_MSG)
        await AskerStatesGroup.next()
    else:
        await message.reply(INVALID_CODE_MSG)

@dp.message_handler(state=AskerStatesGroup.question)
async def load_question(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['question'] = message.text
    await aqt_db.create_new_interviewer(message.chat.id, message.message_id, data["thread_id"])
    user_id = await aqt_db.get_user_id("interviewee", data['thread_id'])
    await bot.send_message(chat_id=user_id[0],
                           text=f"U got a question from {data['thread_id']}'s thread\n\n{data['question']}"
                                f"{CHOOSE_REACTION_MSG}"
                                ,
                           reply_markup=get_answer_ikb())


    await message.reply(f"Okay, I sent ur message to {data['thread_id']} thread.", # If u need to delete it, push on reaction.",
                        reply_markup=get_start_kb())
    await state.finish()


@dp.message_handler(state=ThreadOwnerStatesGroup.answer)
async def load_answer(message: types.Message, state: FSMContext):
    code = await aqt_db.get_thread_id(message.chat.id)
    user_id = await aqt_db.get_user_id("interviewer", code[0])
    await bot.send_message(chat_id=user_id[0],
                           text=f"U got an answer from {code[0]} thread:\n\n"
                                f"{message.text}",
                           reply_markup=get_start_kb())
    await message.reply(text=SENT_ANSWER_MSG,
                        reply_markup=get_start_kb())
    await state.finish()



@dp.callback_query_handler(lambda callback_query: callback_query.data in ["accept", "cancel"])
async def log_accept_handler(callback: types.CallbackQuery):
    await callback.message.delete()
    if callback.data == "accept":
        await callback.message.answer(text=START_MSG,
                        reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.answer(text=NO_LOGS_MSG)
    await callback.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data in ["answer", "skip"])
async def get_answer_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    code = await aqt_db.get_thread_id(callback.message.chat.id)
    chat_id = await aqt_db.get_user_id("interviewee", code[0])
    if callback.data == "answer":
        await callback.message.answer(text=WAIT_ANSWER_MSG)
        await ThreadOwnerStatesGroup.answer.set()
    elif callback.data == "skip":
        await callback.bot.send_message(chat_id=chat_id[0],
                                        text=IGNORE_QUESTION_MSG)
        await callback.message.answer(SENT_IGNORE_MSG)

@dp.errors_handler(exception=BotBlocked)
async def bot_was_blocked(update: types.Update, exception=BotBlocked) -> bool:
    print(ERROR_BOT_WAS_BANNED_MSG)
    return True


if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
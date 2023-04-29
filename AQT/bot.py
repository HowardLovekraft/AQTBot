import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IsReplyFilter
from aiogram.dispatcher.filters.state import StatesGroup, State

import database.aqt_db as aqt_db
from keyboards.keyboards import *
from other.messages import *
from other.code_generator import generator


load_dotenv(dotenv_path="venv.env")

TOKEN_API = getenv('TOKEN_API')
storage = MemoryStorage()
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot,
                storage=storage)


class ThreadOwnerStatesGroup(StatesGroup):
    question = State()

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
    await message.delete()
    await message.answer(text=ACCEPT_LOGS_MSG,
                         reply_markup=get_accept_ikb())


@dp.message_handler(commands=['cancel'], state= '*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await message.delete()
    if state is None:
        return
    await state.finish()
    await message.answer(CANCEL_MSG, reply_markup=get_start_kb())



@dp.message_handler(Text("Create a new thread"), state='*')
async def create_aqt(message: types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    THREAD_ID = await generator()
    while await aqt_db.create_new_thread(message.chat.id, THREAD_ID) == False:
        THREAD_ID = await generator()
        await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    else:
        await message.answer(text=f"Okay, ur thread's ID is {THREAD_ID}"
                                  f"\nSend ur ID to ur friends and get anonymous questions!")
    await ThreadOwnerStatesGroup.question.set()

@dp.message_handler(Text("Write into exist thread"), state='*')
async def work_aqt(message: types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    await message.answer(text=WAIT_CODE_MSG,
                         reply_markup=get_cancel_kb())
    await AskerStatesGroup.number.set()


@dp.message_handler(state=AskerStatesGroup.number)
async def check_and_load_id(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    if await aqt_db.check_thread_id(message.text):
        async with state.proxy() as data:
            data['thread_id'] = message.text
        await message.answer(WAIT_QUESTION_MSG)
        await AskerStatesGroup.next()
    else:
        await message.answer(INVALID_CODE_MSG)

@dp.message_handler(state=AskerStatesGroup.question)
async def load_question(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    async with state.proxy() as data:
        data['question'] = message.text
    user_id = await aqt_db.get_user_id("interviewee", data['thread_id'])
    question = await bot.send_message(chat_id=user_id[0],  # it needs because user_id is a tuple
                                      text=f"U got a question from {data['thread_id']}'s thread\n\n{data['question']}"
                                      f"\n\nTo answer on question, сlick on ✅\n\nIf u don't want to answer, "
                                      f"but need to give feedback, click on ❌",
                                      reply_markup=get_answer_kb())

    await aqt_db.create_new_interviewer(question.chat.id, question.message_id, data['thread_id'])
    await message.answer(f"Okay, I sent ur message to {data['thread_id']} thread.",  # If u need to delete it, push on reaction.",
                        reply_markup=get_start_kb())                                 # don't forget about replying and deleting
    await state.finish()



@dp.callback_query_handler(lambda callback_query: callback_query.data == "accept" or "cancel")
async def log_accept_handler(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    if callback.data == "accept":
        await callback.message.answer(text=START_MSG,
                        reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.answer(text=NO_LOGS_MSG)


@dp.callback_query_handler(lambda callback_query: callback_query.data == "✅" or "❌")
async def accept_answer_handler(callback: types.CallbackQuery, message: types.Message, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    if callback.data == "✅":
        await bot.send_message(chat_id=message.chat.id,
                               text=f"You got an answer from {data['thread_id']}'s thread.\n\n{message.text}")
    elif callback.data == "❌":
        await bot.send_message(chat_id=message.chat.id,
                               text=f"{data['thread_id']}'s thread owner saw your message and wished to ignore it")

@dp.errors_handler(exception=BotBlocked)
async def bot_was_blocked(update: types.Update, exception=BotBlocked) -> bool:
    print(ERROR_BOT_WAS_BANNED_MSG)
    return True


if __name__ == "__main__":
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
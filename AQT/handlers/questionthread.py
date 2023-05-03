import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.filters import Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import AQT.database.aqt_db as aqt_db
from AQT.keyboards.keyboards import *
from AQT.other.messages import *
from AQT.other.code_generator import generator
from AQT.env.env_reader import get_token


router = Router()
bot = Bot(token=get_token())


class ThreadOwner(StatesGroup):
    question = State()
    answer = State()

class ThreadAsker(StatesGroup):
    number = State()
    question = State()


@router.message(Text(GET_START_KB_CREATE))
async def create_aqt(message: Message):
    THREAD_ID = await generator()
    await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    await message.answer(text=f"{CREATE_AQT_MSG} {THREAD_ID}"
                              f"\n{CREATE_THREAD_MSG}")


@router.message(Text(GET_START_KB_WRITE))
async def work_aqt(message: Message, state: FSMContext):
    await message.answer(text=WAIT_CODE_MSG,
                         reply_markup=get_cancel_kb())
    await state.set_state(ThreadAsker.number)


@router.message(ThreadAsker.number, F.text)
async def check_and_load_id(message: Message, state: FSMContext):
    if await aqt_db.check_thread_id(message.text):
        data = await state.get_data()
        data['thread_id'] = message.text
        await state.set_data(data)
        await message.reply(WAIT_QUESTION_MSG)
        await state.set_state(ThreadAsker.question)
    else:
        await message.reply(INVALID_CODE_MSG)

@router.message(ThreadAsker.question)
async def load_question(message: Message, state: FSMContext):
    data = await state.get_data()
    data['question'] = message.text
    await state.set_data(data)
    await aqt_db.create_new_interviewer(message.chat.id, message.message_id, data["thread_id"])
    user_id = await aqt_db.get_user_id(INTERVIEWEE_MODE, data['thread_id'])
    await bot.send_message(chat_id=user_id[0],
                           text=f"{LOAD_QUESTION_FIRST} {data['thread_id']} {LOAD_QUESTION_SECOND}"
                                f"\n\n{data['question']}\n\n{CHOOSE_REACTION_MSG}",
                           reply_markup=get_answer_ikb())


    await message.reply(f"{LOAD_QUESTION_THIRD} {data['thread_id']} {LOAD_QUESTION_FOURTH}", # If u need to delete it, push on reaction.",
                        reply_markup=get_start_kb())
    await state.clear()


@router.message(ThreadOwner.answer)
async def load_answer(message: Message, state: FSMContext):
    code = await aqt_db.get_thread_id(message.chat.id)
    user_id = await aqt_db.get_user_id(INTERVIEWER_MODE, code[0])
    await bot.send_message(chat_id=user_id[0],
                           text=f"{LOAD_ANSWER_FIRST} {code[0]} {LOAD_ANSWER_SECOND}\n\n"
                                f"{message.text}",
                           reply_markup=get_start_kb())
    await message.reply(text=SENT_ANSWER_MSG,
                        reply_markup=get_start_kb())
    await state.clear()



@router.callback_query(lambda callback_query: callback_query.data in ["accept", "cancel"])
async def log_accept_handler(callback: CallbackQuery):
    await callback.message.delete()
    if callback.data == "accept":
        await callback.message.answer(text=START_MSG,
                        reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.answer(text=NO_LOGS_MSG)
    await callback.answer()


@router.callback_query(lambda callback_query: callback_query.data in ["answer", "skip"])
async def get_answer_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    code = await aqt_db.get_thread_id(callback.message.chat.id)
    chat_id = await aqt_db.get_user_id(INTERVIEWEE_MODE, code[0])
    if callback.data == "answer":
        await callback.message.answer(text=WAIT_ANSWER_MSG)
        await state.set_state(ThreadOwner.answer)
    elif callback.data == "skip":
        await bot.send_message(chat_id=chat_id[0],
                               text=IGNORE_QUESTION_MSG)
        await callback.message.answer(SENT_IGNORE_MSG)

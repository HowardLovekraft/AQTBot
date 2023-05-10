from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

import AQT.database.aqt_db as aqt_db
from AQT.keyboards.keyboards import get_start_kb, get_cancel_kb, get_answer_ikb
from AQT.other.messages import *
from AQT.other.code_generator import generator
from AQT.env.env_reader import get_token

# register bot and router
router = Router()
bot = Bot(token=get_token())

i18n = I18n(path="locales", default_locale="en", domain="messages")
i18n_middleware = SimpleI18nMiddleware(i18n)
router.message.outer_middleware(i18n_middleware)
router.callback_query.middleware(i18n_middleware)


# register states
class ThreadOwner(StatesGroup):
    answer = State()


class ThreadAsker(StatesGroup):
    number = State()
    question = State()


@router.message(Text(__("Create a new one")))
async def create_aqt(message: Message) -> None:
    THREAD_ID = await generator()
    await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    await message.answer(text=_("Okay, your thread's ID is `{THREAD_ID}`\nSend your ID to your"
                                "friends and get anonymous questions!\n"
                                "(You can copy the ID by click on it)").format_map({
        "THREAD_ID": "%(THREAD_ID)s"}) % {"THREAD_ID": THREAD_ID},
                         parse_mode="Markdown")


@router.message(Text(__("Write into exist one")))
async def work_aqt(message: Message, state: FSMContext) -> None:
    await message.answer(text=_("Okay, write the thread's ID:\n(you should got it already)"),
                         reply_markup=get_cancel_kb())
    await state.set_state(ThreadAsker.number)


@router.message(ThreadAsker.number, F.text)
async def check_and_load_id(message: Message, state: FSMContext) -> None:
    if await aqt_db.check_thread_id(message.text):
        data = await state.get_data()
        data['thread_id'] = message.text
        await state.set_data(data)
        await message.reply(_("Okay, write a question ^-^"))
        await state.set_state(ThreadAsker.question)
    else:
        await message.reply(_("This code doesn't exist in DB. Type valid code"))


# for future - cut this half of doc and move to another file
@router.message(ThreadAsker.question)
async def load_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data['question'] = message.text
    await state.set_data(data)
    await aqt_db.create_new_interviewer(message.chat.id, message.message_id, data["thread_id"])
    user_id = await aqt_db.get_user_id(INTERVIEWEE_MODE, data['thread_id'])
    await bot.send_message(chat_id=user_id[0],
                           text=_("You got a question from {data} thread\n\n{message}"
                                  "\n\nClick on ✅ to answer on question.\n"
                                  "Click on ❌ if you don't want to answer, but need give "
                                  "feedback.").format_map({
                               "data": "%(data)s",
                               "message": "%(message)s"}) % {"data": data['thread_id'],
                                                             "message": data['question']},
                           parse_mode="Markdown",
                           reply_markup=get_answer_ikb())

    await message.reply(text=_("Okay, I sent your message to {data} thread").format_map({
        "data": "%(data)s"}) % {"data": data['thread_id']},
                        reply_markup=get_start_kb())
    await state.clear()


@router.message(ThreadOwner.answer)
async def load_answer(message: Message, state: FSMContext) -> None:
    code = await aqt_db.get_thread_id(message.chat.id)
    user_id = await aqt_db.get_user_id(INTERVIEWER_MODE, code[0])
    await bot.send_message(chat_id=user_id[0],
                           text=_("You got an answer from {code} thread\n\n{message}").format_map({
        "code": "%(code)s",
        "message": "%(message)s"
}) % {"code": code[0],
      "message": message.text},
                           parse_mode="Markdown",
                           reply_markup=get_start_kb())
    await message.reply(text=_("Okay, I sent your answer"),
                        reply_markup=get_start_kb())
    await state.clear()


@router.callback_query(lambda callback_query: callback_query.data in ["accept", "cancel"])
async def log_accept_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    if callback.data == "accept":
        await callback.message.answer(text=_("Do you want to create a new question "
                                           "thread's link or write a question to "
                                           "the already exist thread?"),
                                      reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.answer(text=_("Okay, but you can't use this bot without "
                                           "logging.\nType /start if you want to start "
                                           "use this bot and accept logging"))
    await callback.answer()


@router.callback_query(lambda callback_query: callback_query.data in ["answer", "skip"])
async def get_answer_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.delete()
    code = await aqt_db.get_thread_id(callback.message.chat.id)
    chat_id = await aqt_db.get_user_id(INTERVIEWEE_MODE, code[0])
    if callback.data == "answer":
        await callback.message.answer(text=_("Okay, write an answer:"))
        await state.set_state(ThreadOwner.answer)
    elif callback.data == "skip":
        await bot.send_message(chat_id=chat_id[0],
                               text=_("Your question has been watched by thread owner, "
                                      "but he preferred to ignore it."))
        await callback.message.answer(text=_("Okay, I sent your feedback"))

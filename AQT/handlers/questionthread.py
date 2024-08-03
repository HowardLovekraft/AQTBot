from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __


import database.postgre_db as aqt_db
from keyboards.keyboards import get_start_kb, get_answer_ikb, get_cancel_kb
from other.messages import *
from other.code_generator import generator
from main import env_vars, i18n_middleware


bot = Bot(token=env_vars.token)
router = Router()

router.message.outer_middleware(i18n_middleware)
router.callback_query.middleware(i18n_middleware)

class ThreadOwner(StatesGroup):
    question = State()
    answer = State()

class ThreadAsker(StatesGroup):
    number = State()
    question = State()


@router.message(F.text == __('Создать новую ветку'))
async def create_aqt(message: Message):
    THREAD_ID = await generator()
    await aqt_db.create_new_thread(message.chat.id, THREAD_ID)
    await message.answer(text=_("Окей, твой ID ветки - `{THREAD_ID}`\nОтправь ID своим друзьям и получай анонимные вопросы!".format(THREAD_ID=THREAD_ID)),
                         parse_mode="Markdown")


@router.message(F.text == __('Написать в существующую ветку'))
async def work_aqt(message: Message, state: FSMContext):
    await message.answer(text=_("Окей, введи ID ветки\n(он у тебя уже должен быть)"),
                         reply_markup=get_cancel_kb())
    await state.set_state(ThreadAsker.number)


@router.message(ThreadAsker.number, F.text)
async def check_and_load_id(message: Message, state: FSMContext):
    if await aqt_db.check_thread_id(message.text):
        data = await state.get_data()
        data['thread_id'] = message.text
        await state.set_data(data)
        await message.reply(_("Окей, введи вопрос ^-^"))
        await state.set_state(ThreadAsker.question)
    else:
        await message.reply(_("Этого кода нет в базе данных. Введи существующий код"))

@router.message(ThreadAsker.question)
async def load_question(message: Message, state: FSMContext):
    data = await state.get_data()
    data['question'] = message.text
    await state.set_data(data)
    await aqt_db.create_new_asker(asker_chat_id=message.chat.id,
                                  question_msg_id=message.message_id,
                                  thread_code=data["thread_id"])
    user_id = await aqt_db.get_user_id(OWNER_MODE, data['thread_id'])
    await bot.send_message(chat_id=user_id[0],
                           text=_("Ты получил вопрос в ветке `{data}`\n\n{message}\n\n"
                                  "Кликни на ✅, чтобы ответить на вопрос.\n"
                                  "Кликни на ❌, если не хочешь отвечать, но хочешь отправить факт просмотра."
                                  .format(data=data['thread_id'],
                                          message=data["question"])),
                           parse_mode="Markdown",
                           reply_markup=get_answer_ikb())


    await message.reply(text=_("Окей, я отправил твоё сообщение в ветку `{data}`."
                                     .format(data=data['thread_id'])),
                        parse_mode="Markdown",
                        reply_markup=get_start_kb())
    await state.clear()


@router.message(ThreadOwner.answer)
async def load_answer(message: Message, state: FSMContext):
    code = await aqt_db.get_thread_id(message.chat.id)
    user_id = await aqt_db.get_user_id(ASKER_MODE, code[0])
    await bot.send_message(chat_id=user_id[0],
                           text=_("Ты получил ответ из ветки `{code}`\n\n{message}".format(code=code[0], message=message.text)),
                           parse_mode="Markdown",
                           reply_markup=get_start_kb())
    await message.reply(text=_("Окей, я отправил твой ответ"),
                        reply_markup=get_start_kb())
    await state.clear()



@router.callback_query(lambda callback_query: callback_query.data in ["accept", "cancel"])
async def log_accept_handler(callback: CallbackQuery):
    await callback.message.delete()
    if callback.data == "accept":
        await callback.message.answer(text=_("Хочешь создать новую ветку вопросов или написать вопрос в существующую ветку?"),
                                      reply_markup=get_start_kb())
    elif callback.data == "cancel":
        await callback.message.answer(text="Привет! Для начала работы, тебе нужно подтвердить логгирование твоего ID и ID твоих сообщений.\n"
                                             "Все другие данные (сообщения, их контент и т.д.) не логгируются")
    await callback.answer()


@router.callback_query(lambda callback_query: callback_query.data in ["answer", "skip"])
async def get_answer_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    code = await aqt_db.get_thread_id(callback.message.chat.id)
    chat_id = await aqt_db.get_user_id(OWNER_MODE, code[0])
    if callback.data == "answer":
        await callback.message.answer(text=_("Окей, напиши ответ"))
        await state.set_state(ThreadOwner.answer)
    elif callback.data == "skip":
        await bot.send_message(chat_id=chat_id[0],
                               text=_("Твой вопрос был просмотрен создателем ветки, но он предпочел не отвечать на него."))
        await callback.message.answer(_("Окей, я отправлю твою реакцию"))
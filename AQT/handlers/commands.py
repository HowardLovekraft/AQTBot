from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from AQT.keyboards.keyboards import *
from aiogram.utils.i18n import I18n, gettext, SimpleI18nMiddleware


router = Router()
i18n = I18n(path="locales", default_locale="en", domain="messages")
router.message.middleware(SimpleI18nMiddleware(i18n))

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(text=gettext("Hi! To start working, u need to accept "
                                      "logging your user_id and your messages' "
                                      "ids.\nAll other data(messages, their "
                                      "content etc.) is not subject to logging"),
                         reply_markup=get_accept_ikb())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if state is None:
        return
    await state.clear()
    await message.reply(text=gettext("You canceled the process"),
                        reply_markup=get_start_kb())

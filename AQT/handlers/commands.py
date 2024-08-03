from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from keyboards.keyboards import get_accept_ikb, get_start_kb
from main import i18n_middleware


router = Router()
router.message.middleware(i18n_middleware)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(text=_("Hi! To start working, u need to accept "
                                      "logging your user_id and your messages' "
                                      "ids.\nAll other data(messages, their "
                                      "content etc.) is not subject to logging"),
                         reply_markup=get_accept_ikb())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if state is None:
        return
    await state.clear()
    await message.reply(text=_("You canceled the process"),
                        reply_markup=get_start_kb())

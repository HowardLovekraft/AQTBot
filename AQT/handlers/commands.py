from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from AQT.keyboards.keyboards import *

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(text=ACCEPT_LOGS_MSG,
                         reply_markup=get_accept_ikb())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if state is None:
        return
    await state.clear()
    await message.reply(CANCEL_MSG, reply_markup=get_start_kb())

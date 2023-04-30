from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Create a new thread"), KeyboardButton(text="Write into exist thread")]
    ])
    return kb


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/cancel'))
    return kb

def get_accept_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Accept",
                              callback_data="accept"),

         InlineKeyboardButton(text="Cancel",
                              callback_data="cancel")]
    ])
    return ikb

def get_answer_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅",
                              callback_data="answer"),
         InlineKeyboardButton(text="❌",
                             callback_data="skip")]
    ])
    return ikb


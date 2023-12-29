from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from main import text_msgs


def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("Create a new one"))
    kb.button(text=_('Write into exist one'))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='/cancel')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def get_accept_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text=_('Accept'),
               callback_data="accept")
    ikb.button(text=_('Cancel'),
               callback_data="cancel")
    ikb.adjust(2)
    return ikb.as_markup()

def get_answer_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text=text_msgs["GET_ANSWER_IKB_ANSWER"], callback_data="answer")
    ikb.button(text=text_msgs["GET_ANSWER_IKB_SKIP"], callback_data="skip")
    ikb.adjust(2)
    return ikb.as_markup()

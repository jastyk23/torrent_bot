from typing import Final
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

KB_SETUP: Final = InlineKeyboardMarkup(inline_keyboard=[
    InlineKeyboardButton(text="Принять", callback_data="set_setup"),
    InlineKeyboardButton(text="Отменить", callback_data="cancel_setup")
])



from typing import Final
from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    ADMIN: Final = State()
    INSERT_NEW_ADMIN: Final = State()
    INSERT_ADVERT_TEXT: Final = State()
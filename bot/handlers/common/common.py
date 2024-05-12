from os import environ

from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from pyrogram import Client


router = Router()


async def _input_phone(message: Message, state: FSMContext) -> None:
    bot: Bot = state.get_data()
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    try:
        client = Client(
            name=str(message.from_user.id),
            api_id=environ["API_ID"],
            api_hash=environ["API_HASH"],
            in_memory=True,
        )
        await client.connect()
    except Exception as e:
        await bot.send_message(user_id, f"Не удалось отправить смс! ⚠️\nПопробуйте еще раз!" +
                               "<i>Если проблема остаеться, обратитесь в тех поддержку, или попробуйте с мобильного " +
                               "устройства")
        await state.clear()
        return


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я помогу тебе найти торрент и скачать его")

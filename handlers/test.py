from aiogram import types

from create_bot import dp


@dp.message_handler(commands=["test"])
async def test_cmd(message: types.Message):
    await message.answer('test')

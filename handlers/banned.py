import time

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import MessageCantBeDeleted

from filters import IsUserBanned
from handlers.parser import memes
import config as cfg
from create_bot import bot
from database.db import User


async def banned_user_com(message: types.Message):
    if message.chat.id in cfg.data:
        if 'command' != cfg.data[message.chat.id].ban_rule:
            await banned_user_message(message)
            return
    await message.answer('А я думал ты сдох...\nПосмотри пока котиков, отдохни')
    mem = await memes.get_cat()
    await bot.send_animation(chat_id=message.chat.id, animation=mem)


async def banned_user_message(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        await message.answer('Эх, был бы я администратором, хрен бы ты у меня из бана вылез! =)')
        

async def callback_banned(call: types.CallbackQuery):
    user: User = cfg.data[call.message.chat.id].users[call.from_user.id]
    await call.answer(f'Ты забанен!\nОсталось {user.ban_time - time.time():.0f} секунд', show_alert=True)


def register_banned_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        banned_user_com, IsUserBanned(), Command(commands=['p', "c", 'm', 'mem', 'rename', 'hit', 'dice']))
    dp.register_message_handler(banned_user_message, IsUserBanned())
    dp.register_callback_query_handler(callback_banned, IsUserBanned())
    
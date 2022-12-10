import sqlite3

from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram import types

from create_bot import bot, rate_limit
from database.db import User

import config as cfg


@rate_limit(60, 'rename')
async def cmd_rename(message: types.Message):

    if not message.get_args():
        return

    try:
        await message.delete()
    except (MessageCantBeDeleted, MessageToDeleteNotFound):
        pass

    name = str(message.get_args())
    if len(name) > 40:
        await message.answer('Ебись конём отсюда. Ограничение по длине 40 символов')
        return
    if '<' in name or '>' in name or '&' in name:
        await message.answer('Сорян символы "<", ">" и "&" не принимаются')
        return

    base = sqlite3.connect('sql/hit.db')
    cur = base.cursor()
    try:
        y = cur.execute(f'SELECT user_id FROM stat WHERE name = ? AND chat_id = ?',
                        (name, message.chat.id)).fetchone()
        if y:
            zanyato = await bot.get_chat_member(message.chat.id, y[0])
            await message.answer(f'Это имя себе уже выбрал {zanyato.user.first_name}')
            base.close()
            return
    except sqlite3.Error:
        print('Не нашёл такое имя или какая-то ошибка')
    base.close()

    user = cfg.data[message.chat.id].users.get(message.from_user.id, User(message.from_user, message.chat.id))
    user.name = name
    user.update()
    await message.answer(f'Теперь ты будешь - {name}')

from aiogram.utils.exceptions import MessageCantBeDeleted
from aiogram import types

import config as cfg

from database.db import User


async def cmd_stat(message: types.Message):

    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    user: User = cfg.data[message.chat.id].users.get(message.from_user.id, User(message.from_user, message.chat.id))
    wpn_str = f'Прочность: {user.weapon.durability}\nУрон: {user.weapon.dmg}\n' if user.weapon.durability else ''
    await message.answer(
        f'{user.tag} 💪{user.hp} HP:\nУрон 👊 {user.atack}\n'
        f'Оружие: {user.weapon.pic} {user.weapon.name}\n'
        f'{wpn_str}'
        f'Отправил в бан {user.uebal} человек',
        parse_mode="HTML"
    )


async def cmd_stat_all(message: types.Message):

    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    msg_stat = ''
    for user in list(cfg.data[message.chat.id].users.values())[:10]:
        msg_stat += f'{user.tag}\n{user.weapon.name}: {user.weapon.dmg}\nУрон: {user.atack}, {user.hp} HP\n{"-"*10}\n'

    await message.answer(msg_stat, parse_mode="HTML")

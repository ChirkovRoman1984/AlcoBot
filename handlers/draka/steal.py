import asyncio
import copy
import logging
import random
import time

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

import config as cfg
from create_bot import rate_limit
from database.db import User
from dialogs import msg


@rate_limit(60, 'steal')
async def cmd_steal(message: types.Message):

    if not message.reply_to_message:
        return

    chat_id = message.chat.id
    thief: User = cfg.data[chat_id].users.get(message.from_user.id, User(message.from_user, chat_id))
    user: User = cfg.data[chat_id].users.get(
        message.reply_to_message.from_user.id, User(message.reply_to_message.from_user, chat_id))

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Отпугнуть', callback_data='dont_steal'))
    steal_msg = await message.reply(
        f'Пока {user.tag} отдыхает, у него в кармане копается {thief.tag}',
        parse_mode='HTML',
        disable_notification=True,
        reply_markup=markup)

    await asyncio.sleep(20)

    if thief.cant_steal:
        thief.cant_steal = False
        return

    try:
        await steal_msg.delete_reply_markup()
    except MessageNotModified:
        pass

    weapon = copy.copy(user.weapon)
    if random.randint(1, 2) < 2:
        thief.weapon = weapon
        user.weapon.durability = 0
        thief.update()
        user.update()
        logging.info(msg=f'{weapon.name}@{weapon.dmg}@{weapon.durability} спиздил {thief.id} у {user.id}')
        await message.answer(
            f'{thief.tag} удачно стащил {weapon.name}, урон - {weapon.dmg}, прочность - {weapon.durability}',
            parse_mode="HTML")
    else:
        await message.answer(f'{thief.tag} не смог ничего стащить', parse_mode='HTML')


async def callback_inline_steal(call: types.CallbackQuery):
    try:
        await call.message.delete_reply_markup()
    except MessageNotModified:
        return

    chat_id = call.message.chat.id
    user1: User = cfg.data[chat_id].users.get(call.from_user.id, User(call.from_user, chat_id))
    user2: User = cfg.data[chat_id].users[call.message.reply_to_message.from_user.id]

    # await bot.send_message(chat_id=chat_id, text=f'{user2.name} - воришка')
    user1.weapon.durability -= 1
    user2.hp -= user1.atack

    otvet = f"{user1.name} {random.choice(msg.hit_low)}, чтобы " \
            f"{user2.name} не шарил по карманам.\n{user2.name} получил минус {user1.atack} HP"
    if user2.hp == 0:
        user2.hp = 100
        user1.uebal += 1
        otvet = f'{otvet} и сдох. Бан ему на {int(cfg.time_ban)} секунд'
        user2.ban_time = int(time.time()) + cfg.time_ban
    await call.message.reply_to_message.reply(otvet)
    user1.update()
    user2.update()
    user2.cant_steal = True


def register_handlers_steal(disp: Dispatcher):
    disp.register_message_handler(cmd_steal, commands='steal')


def register_callback_steal(disp: Dispatcher):
    disp.register_callback_query_handler(callback_inline_steal, Text(startswith=['dont_steal']))

import logging
import random
import time

from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

import config as cfg
from database.db import User


food_emoji = (
        '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐ฅญ', '๐', '๐ฅฅ', '๐ฅ', '๐', '๐ฅ', '๐', '๐ถ',
        '๐ฅ', '๐ฅฌ', '๐ฅฆ', '๐ง', '๐ง', '๐ฝ', '๐ฅ', '๐ฅ', '๐ฅ', '๐ ', '๐ฐ', '๐ฅ', '๐ฏ', '๐', '๐ฅ', '๐ฅ', '๐ฅจ', '๐ฅฏ', '๐ฅ', '๐ง',
        '๐ง', '๐', '๐', '๐ฅฉ', '๐ค', '๐ฅ', '๐ณ', '๐ฅ', '๐', '๐', '๐ญ', '๐', '๐', '๐ฅช', '๐ฎ', '๐ฏ', '๐ฅ', '๐ง', '๐', '๐ฅ',
        '๐ฒ', '๐ฅซ', '๐ง', '๐ง', '๐ฅ', '๐ฃ', '๐ฑ', '๐', '๐', '๐', '๐', '๐ฅ', '๐ข', '๐ก', '๐ง', '๐จ', '๐ฆ', '๐ฐ', '๐', '๐ง',
        '๐ฅง', '๐ฎ', '๐ญ', '๐ฌ', '๐ซ', '๐ฟ', '๐ฉ', '๐ช', '๐ฅ ', '๐ฅฎ', 'โ', '๐ต'
    )


async def show_snack(message: types.Message, start=-40, stop=100):
    hp = random.randrange(start, stop, 5)
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton("ะะฐะฒะฐะน!", callback_data=f'hp:{hp}')
    markup.add(item)
    await message.answer(f'{random.choice(food_emoji)}')
    await message.answer(f'ะะพะผั ะฒะบััะฝััะบั?', reply_markup=markup)


async def callback_inline_snack(call: types.CallbackQuery):
    try:
        await call.message.delete_reply_markup()
    except MessageNotModified:
        return

    user: User = cfg.data[call.message.chat.id].users.get(call.from_user.id, User(call.from_user, call.message.chat.id))
    hp = int(call.data.split(':')[1])
    user.hp += hp
    await call.message.edit_text(
        f'{user.name} ััะตะป ะฒะบััะฝััะบั {"ัะดะพะฒะธััั" if hp < 0 else ""} ะฝะฐ {hp}HP, ัะตะฟะตัั ั ะฝะตะณะพ {user.hp}HP')
    if user.hp == 0:
        user.hp = 100
        user.ban_time = int(time.time()) + cfg.time_ban
        await call.message.answer(f'{user.name}, ะฑะฐะฝ ัะตะฑะต ะฝะฐ {cfg.time_ban} ัะตะบัะฝะด โ ๏ธโ ๏ธ')
    user.update()

    log_msg = f'FOOD ----- {call.data} --> chat_id={call.message.chat.id}, user_id={call.from_user.id} - {user.name}'
    logging.info(msg=log_msg)

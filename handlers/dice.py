import asyncio
import logging
import random
import time

from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageNotModified

import config as cfg
from handlers.draka import food

from create_bot import dp, rate_limit
from database.db import User


@rate_limit(30, 'dice')
async def cmd_dice(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    user: User = cfg.data[message.chat.id].users.get(message.from_user.id, User(message.from_user, message.chat.id))
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in [10, 20, 50, 100, 500]:
        if i < user.hp:
            button = types.InlineKeyboardButton(text=str(i), callback_data=f'dice@{i}')
            buttons.append(button)
    if user.hp > 1:
        buttons.append(types.InlineKeyboardButton(text='Все слить, кроме 1 HP', callback_data=f'dice@{user.hp - 1}'))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton(text="Отмена", callback_data=f"dice@0"))
    await message.answer(f'У тебя есть {user.hp} HP. Твоя ставка?', reply_markup=markup)


async def callback_inline_dice(call: types.CallbackQuery):
    try:
        await call.message.delete_reply_markup()
    except MessageNotModified:
        return
    user = cfg.data[call.message.chat.id].users.get(call.from_user.id, User(call.from_user, call.message.chat.id))
    stavka = int(call.data.split('@')[1])
    if stavka == 0:
        return
    await call.message.edit_text(f'{user.name}: Ставка {stavka} HP')
    log_msg = f'DICE ----- chat={user.chat_id}, user={user.id} - {user.name}, ставка={stavka}'

    user.hp -= stavka

    if user.hp == 0:
        user.hp = 100
        user.ban_time = int(time.time()) + 2 * cfg.time_ban
        await call.message.answer(f'Бан тебе на {int(2 * cfg.time_ban)} секунд ☠️☠️☠️ за то, что проебал всё HP')
        log_msg += ' Проебал всё ХП'
        logging.info(msg=log_msg)
        user.update()
        return

    val = await dp.bot.send_dice(chat_id=call.message.chat.id, emoji='🎰')

    bonus = 0
    # Джэкпот
    if val['dice']['value'] in [1, 22, 43, 64]:
        bonus = stavka * random.randrange(6, 8)

    # один бар и 2 одинаковые
    elif val['dice']['value'] in [6, 11, 16, 18, 21, 35, 41, 52, 61]:
        bonus = stavka * random.randrange(3, 4)

    # Два Бара
    elif val['dice']['value'] in [2, 3, 4, 5, 9, 13, 17, 33, 49]:
        bonus = stavka

    if bonus:
        user.hp += bonus
        user.update()
        log_msg += f', выигрыш={bonus}'
        await asyncio.sleep(3)
        await call.answer(f'Выигрыш {bonus} hp', show_alert=True)
        await call.message.answer('Бонусная вкусняшка в честь победителя!')
        await food.show_snack(call.message, start=0, stop=40)

    else:
        user.update()
        log_msg += f', проебал'
        await asyncio.sleep(3)
        await call.answer('Казино не наебёшь!', show_alert=False)

    logging.info(msg=log_msg)


slot_machine_value = {
    1: ("bar", "bar", "bar"),
    2: ("grape", "bar", "bar"),
    3: ("lemon", "bar", "bar"),
    4: ("seven", "bar", "bar"),
    5: ("bar", "grape", "bar"),
    6: ("grape", "grape", "bar"),
    7: ("lemon", "grape", "bar"),
    8: ("seven", "grape", "bar"),
    9: ("bar", "lemon", "bar"),
    10: ("grape", "lemon", "bar"),
    11: ("lemon", "lemon", "bar"),
    12: ("seven", "lemon", "bar"),
    13: ("bar", "seven", "bar"),
    14: ("grape", "seven", "bar"),
    15: ("lemon", "seven", "bar"),
    16: ("seven", "seven", "bar"),
    17: ("bar", "bar", "grape"),
    18: ("grape", "bar", "grape"),
    19: ("lemon", "bar", "grape"),
    20: ("seven", "bar", "grape"),
    21: ("bar", "grape", "grape"),
    22: ("grape", "grape", "grape"),
    23: ("lemon", "grape", "grape"),
    24: ("seven", "grape", "grape"),
    25: ("bar", "lemon", "grape"),
    26: ("grape", "lemon", "grape"),
    27: ("lemon", "lemon", "grape"),
    28: ("seven", "lemon", "grape"),
    29: ("bar", "seven", "grape"),
    30: ("grape", "seven", "grape"),
    31: ("lemon", "seven", "grape"),
    32: ("seven", "seven", "grape"),
    33: ("bar", "bar", "lemon"),
    34: ("grape", "bar", "lemon"),
    35: ("lemon", "bar", "lemon"),
    36: ("seven", "bar", "lemon"),
    37: ("bar", "grape", "lemon"),
    38: ("grape", "grape", "lemon"),
    39: ("lemon", "grape", "lemon"),
    40: ("seven", "grape", "lemon"),
    41: ("bar", "lemon", "lemon"),
    42: ("grape", "lemon", "lemon"),
    43: ("lemon", "lemon", "lemon"),
    44: ("seven", "lemon", "lemon"),
    45: ("bar", "seven", "lemon"),
    46: ("grape", "seven", "lemon"),
    47: ("lemon", "seven", "lemon"),
    48: ("seven", "seven", "lemon"),
    49: ("bar", "bar", "seven"),
    50: ("grape", "bar", "seven"),
    51: ("lemon", "bar", "seven"),
    52: ("seven", "bar", "seven"),
    53: ("bar", "grape", "seven"),
    54: ("grape", "grape", "seven"),
    55: ("lemon", "grape", "seven"),
    56: ("seven", "grape", "seven"),
    57: ("bar", "lemon", "seven"),
    58: ("grape", "lemon", "seven"),
    59: ("lemon", "lemon", "seven"),
    60: ("seven", "lemon", "seven"),
    61: ("bar", "seven", "seven"),
    62: ("grape", "seven", "seven"),
    63: ("lemon", "seven", "seven"),
    64: ("seven", "seven", "seven"),
}

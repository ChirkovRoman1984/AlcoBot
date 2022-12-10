import copy
import logging
import random
import time
import pymorphy2

from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

import config as cfg

from database.db import User

weapons = {}
morph = pymorphy2.MorphAnalyzer()


class Weapons:

    item: tuple = (
        "призрак 👻", "тыква 🎃", "говно 💩", "киборг 🤖", "череп 💀", "протез 🦾", "зомбак 🧟", "кактус 🌵",
        "шприц 💉", 'меч 🗡', 'лук 🏹', 'топор 🪓', 'сабелька ⚔', 'волына 🔫', 'перчатка 🥊',
        'взрывчатка 🧨', 'кирпич 🧱', 'нож 🔪', 'хлопушка 💣'
    )

    pre: tuple = (
        "Краденный", "Новый", "Испорченный", "Блестящий", "Вонючий", "Дерьмовый", "Лагающий", "Вялый", "Опасный",
        "Редкий", "Недоделанный", "Испачканный", "Игрушечный", "Охуенный", "ватный", "мягкий",
        "зелёный", "синий", "красный", "немой", "плесневый", "замухрышевый", "обновлённый", "светлый", "тёмный",
        "сказочный", "бомбический", "топовый", "бомбовый", "тестовый", "толстый", "горбатый",
        "уебанный", "погнутый", "поганый", "анисовый",
        "разработанный", "круглый", "квадратный", "целый", "компьютерный", "мощный", "Теплый", "нужный",
        "временный", "шумный", "свистящий", "гнутый", "треугольный", "прямоугольный", "стволовой",
        "хуеплетский", "уебанский", "изумрудный"
    )

    person: tuple = (
        "алкаш", "бомж", "алкоголик", "гопник", "барыга", "король", "мент", "вампир", "император", "изгой",
        "нарик", "дворник", "мертвец"
    )

    def __init__(self, max_dmg=60, max_durability=30, name='', for_user_id=0):
        weapon = random.choice(self.item)
        pre_w = random.choice(self.pre)
        post_w = random.choice(self.person)
        self.pic = weapon.split()[1]
        gender = [i.tag.gender for i in morph.parse(weapon.split()[0]) if 'NOUN' in i.tag and 'nomn' in i.tag][0]
        if name:
            self.name = name
        else:
            self.name = (
                    morph.parse(pre_w)[0].inflect({gender}).word +
                    ' ' + weapon.split()[0] + ' ' + morph.parse(post_w)[0].inflect({'gent'}).word
            )
        self.dmg = random.randint(5, max_dmg)
        self.durability = random.randint(5, max_durability)
        self.for_user_id = int(for_user_id)
        self.sql_str = f'{self.pic}@{self.name}@{self.dmg}@{self.durability}@{self.for_user_id}'
        self.taked = False


async def weapon_show(message: types.Message, max_dmg=60, max_durability=30, name='', for_user_id=0):
    weapon = Weapons(max_dmg, max_durability, name, for_user_id)
    key = f'{message.chat.id}@{int(time.time())}'
    weapon.key = key
    weapons[key] = weapon
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton("Подобрать", callback_data=f'weapon={key}')
    markup.add(item)
    await message.answer(weapon.pic)
    await message.answer(
        f'{weapon.name}\nПрочность - {weapon.durability}\nУрон - {weapon.dmg}',
        reply_markup=markup
    )


async def weapon_drop(message: types.Message, weapon):
    key = f'{message.chat.id}@{int(time.time())}'
    weapon.key = key
    weapons[key] = weapon
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton("Подобрать", callback_data=f'weapon={key}')
    markup.add(item)
    await message.answer(weapon.pic)
    await message.answer(
        f'{weapon.name}\nПрочность - {weapon.durability}\nУрон - {weapon.dmg}',
        reply_markup=markup
    )


# @dp.message_handler(commands=["pushka"])
async def cmd_pushka(message: types.Message):
    text = message.get_args()
    chat_id, for_user_id, name, max_dmg, max_durability = text.split('@')
    message.chat.id = int(chat_id)
    await weapon_show(message, int(max_dmg), int(max_durability), name, int(for_user_id))


# @dp.callback_query_handler(Text(startswith=['weapon']))
async def callback_weapon(call: types.CallbackQuery):
    key = call.data.split('=')[1]
    weapon = weapons.get(key, None)
    if not weapon:
        await call.answer('Долго валялась эта хрень, ну и проебалась она куда-то...')
        return

    user: User = cfg.data[call.message.chat.id].users.get(call.from_user.id, User(call.from_user, call.message.chat.id))
    if weapon.for_user_id:
        if not weapon.taked and user.id != weapon.for_user_id:
            await call.answer('Не твое, не трогай!')
            return
    
    try:
        await call.message.delete_reply_markup()
    except MessageNotModified:
        return

    user.weapon = copy.copy(weapon)
    user.update()
    await call.answer(
        f'Ты подобрал {weapon.name}\nПрочность: {weapon.durability}\nУрон: {weapon.dmg}', show_alert=True)
    await call.message.edit_text(f'{weapon.name} подобрал {user.name}')
    del weapons[key]

    log_msg = f'WEAPON --- {weapon.name}@{weapon.dmg}@{weapon.durability}' \
              f' --> chat_id={call.message.chat.id}, user_id={call.from_user.id} - {user.name}'
    logging.info(msg=log_msg)

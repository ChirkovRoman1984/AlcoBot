import logging
import random
import time

from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

import config as cfg
from database.db import User


food_emoji = (
        '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🥑', '🍆', '🌶',
        '🥒', '🥬', '🥦', '🧄', '🧅', '🌽', '🥕', '🥗', '🥔', '🍠', '🌰', '🥜', '🍯', '🍞', '🥐', '🥖', '🥨', '🥯', '🥞', '🧇',
        '🧀', '🍗', '🍖', '🥩', '🍤', '🥚', '🍳', '🥓', '🍔', '🍟', '🌭', '🍕', '🍝', '🥪', '🌮', '🌯', '🥙', '🧆', '🍜', '🥘',
        '🍲', '🥫', '🧂', '🧈', '🍥', '🍣', '🍱', '🍛', '🍙', '🍚', '🍘', '🥟', '🍢', '🍡', '🍧', '🍨', '🍦', '🍰', '🎂', '🧁',
        '🥧', '🍮', '🍭', '🍬', '🍫', '🍿', '🍩', '🍪', '🥠', '🥮', '☕', '🍵'
    )


async def show_snack(message: types.Message, start=-40, stop=100):
    hp = random.randrange(start, stop, 5)
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton("Давай!", callback_data=f'hp:{hp}')
    markup.add(item)
    await message.answer(f'{random.choice(food_emoji)}')
    await message.answer(f'Кому вкусняшку?', reply_markup=markup)


async def callback_inline_snack(call: types.CallbackQuery):
    try:
        await call.message.delete_reply_markup()
    except MessageNotModified:
        return

    user: User = cfg.data[call.message.chat.id].users.get(call.from_user.id, User(call.from_user, call.message.chat.id))
    hp = int(call.data.split(':')[1])
    user.hp += hp
    await call.message.edit_text(
        f'{user.name} съел вкусняшку {"ядовитую" if hp < 0 else ""} на {hp}HP, теперь у него {user.hp}HP')
    if user.hp == 0:
        user.hp = 100
        user.ban_time = int(time.time()) + cfg.time_ban
        await call.message.answer(f'{user.name}, бан тебе на {cfg.time_ban} секунд ☠️☠️')
    user.update()

    log_msg = f'FOOD ----- {call.data} --> chat_id={call.message.chat.id}, user_id={call.from_user.id} - {user.name}'
    logging.info(msg=log_msg)

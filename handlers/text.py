import asyncio
import logging
import random

import config as cfg

from aiogram import types
from aiogram.utils.exceptions import BadRequest

from ai.sberbank import text_gen, Dialog, dialogs
from ai.test_class import classifier
from dialogs import msg, prikol
from handlers.draka.food import show_snack
from handlers.draka.weapon import weapon_show
from handlers.parser.bani import show_bani


async def show_random_goodies(message: types.Message):
    rnd = random.randint(1, 100)
    if rnd < 6:
        await weapon_show(message)
    elif 6 <= rnd < 16:
        await show_snack(message)


async def reply_text_messages(message: types.Message):
    if message.reply_to_message.from_user.id == 2070208630 and message.text:
        dialog = dialogs.get(message.chat.id, None)
        if dialog is None:
            dialog = Dialog()
            dialogs[message.chat.id] = dialog
        text_msgs = dialog.text(message)
        otvet = ''
        if text_msgs:
            otvet = text_gen.reply2(text_msgs)
        # otvet = text_gen.reply(message)
        if otvet:
            log_msg = f'{message.chat.title}, {message.chat.id}, {message.from_user.first_name}, {message.text}' \
                      f'\n{otvet}'
            logging.info(msg=log_msg)
            await asyncio.sleep(4)
            await message.reply(otvet)

    await show_random_goodies(message)


async def get_text_messages(message: types.Message):

    await show_random_goodies(message)

    if "алкаш" in message.text.lower():
        msg_text = message.text.lower()
        msg_text = msg_text.replace('алкаш', '')
        if message.from_user.id == 415161688 and random.randrange(0, 3) == 1:
            await show_bani(message)
        if classifier.predict(msg_text):
            variant = random.randrange(0, 3)
            if variant == 1:
                await message.answer('Завалялась тут у меня одна хреновина...')
                await weapon_show(message, max_dmg=20, max_durability=5)
            elif variant == 2:
                await message.answer('Съешь лучше что-нибудь')
                await show_snack(message, start=-50, stop=30)
            else:
                await message.answer('Неее... всё пробухал')
        else:
            await asyncio.sleep(2)
            await message.answer(await prikol.random_string)

    elif cfg.data[message.chat.id].message_counter > 15:
        cfg.data[message.chat.id].message_counter = random.randrange(10)

        if random.randrange(0, 6) == 1:
            sticker = 'stikers\\stick (' + str(random.randrange(1, 242)) + ').webp'
            await asyncio.sleep(2)
            try:
                with open(sticker, 'rb') as stick:
                    await message.answer_sticker(stick)
            except BadRequest:
                await message.answer(
                    'Хотел вам стикер отправить, но у вас тут нельзя это делать =(\n'
                    'Как-то у вас тут уныло... Чувствую себя обделенным')

        elif random.randrange(0, 6) == 2:
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Давай!", callback_data='hit - да')
            item2 = types.InlineKeyboardButton("Пусть живёт", callback_data='hit - нет')
            item3 = types.InlineKeyboardButton('Налить ему и себе по 100 грамм', callback_data='hit - налить')
            markup.add(item1, item2, item3)
            await asyncio.sleep(2)
            await message.reply("Уебать бы тебе за такое. Может кто поможет?", reply_markup=markup)

        else:
            otvet = text_gen.answer(message)
            if otvet:
                log_msg = f'{message.chat.title}, {message.chat.id}, {message.text}\n{otvet}'
                logging.info(msg=log_msg)
                await asyncio.sleep(2)
                await message.reply(otvet)

    # elif "баня" in message.text.lower() and message.chat.id == cfg.GROUP_ID:
    #     # otv1 = generated_text("баня -", max_length=20)
    #     otv1 = text_gen.generate("баня -", max_length=20)
    #     otv2 = text_gen.generate("готовься", max_length=20)
    #     await message.answer(f"[{random.choice(cfg.names[1105830408])}](tg://user?id=1105830408), {otv1}\n"
    #                          f"[{random.choice(cfg.names[149303688])}](tg://user?id=149303688), {otv2}",
    #                          parse_mode="Markdown")

    elif "наливай" in message.text.lower():
        await asyncio.sleep(2)
        await message.reply(random.choice(msg.nalivay))

    cfg.data[message.chat.id].message_counter += 1
    cfg.data[message.chat.id].last_msg_time = message.date.timestamp()

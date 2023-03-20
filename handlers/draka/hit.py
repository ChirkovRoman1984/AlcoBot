import copy
import random
import time
import asyncio
from typing import Dict

from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageNotModified, MessageToDeleteNotFound

import config as cfg
from ai.sberbank import text_gen
from config import data
from database.db import db, User, Chat
from handlers.draka.weapon import weapon_drop
from create_bot import bot, rate_limit
from dialogs import msg


class PollFight:
    def __init__(self, chat_id, poll_id):
        self.voters: list = []
        self.chat_id: int = chat_id
        self.id: int = poll_id


active_polls: Dict[int, PollFight] = {}


@rate_limit(30, 'hit')
async def cmd_hit(message: types.Message):
    await hit(message) if message.reply_to_message else await fight(message)


async def fight(message: types.Message):
    try:
        await message.delete()
    except (MessageCantBeDeleted, MessageToDeleteNotFound):
        pass
    chat: Chat = data[message.chat.id]
    if chat.is_fight_now:
        await message.answer('Обожди')
        return

    imya = db.name(message.from_user, message.chat.id)
    smotrit = await message.answer(f"{imya} разбушевался! Смотрит кому вьебать...")
    options = random.sample(msg.hit, 3)
    msg_poll = await bot.send_poll(
        chat_id=message.chat.id, question=f'"{msg.title}"\nВыбирай как въебать 20 сек.',
        options=options, is_anonymous=False, open_period=20
    )

    poll = PollFight(chat.id, msg_poll.poll.id)
    active_polls[poll.id] = poll

    chat.is_fight_now = msg_poll.poll.open_period

    await asyncio.sleep(20)
    await msg_poll.delete()

    # Проверка забаненых среди проголосовавших
    msg_ban = ''
    for voter_id in list(poll.voters):
        if chat.users[voter_id].banned:
            msg_ban += f'{chat.users[voter_id].tag} ' \
                       f'получает еще 2 минуты бана плюсом ☠️☠️☠️, так как уже был забанен\n'
            chat.users[voter_id].ban_time += cfg.time_ban
            del poll.voters[voter_id]

    if len(poll.voters) == 0:
        await smotrit.edit_text(
            f"{imya} разбушевался! Смотрит кому вьебать...\nНо никого не нашёл")
        if msg_ban:
            await message.answer(msg_ban)
        del active_polls[poll.id]
        return

    if len(poll.voters) == 1:
        voter_id = poll.voters[0]
        user = chat.users[voter_id]
        if user.id == message.from_user.id:
            await smotrit.edit_text(
                f"{imya} разбушевался! Смотрит кому вьебать...\nНо никого не нашёл")
            random_user_id = db.get_random(chat.id, message.from_user.id)
            random_user = await bot.get_chat_member(chat.id, random_user_id)
            random_user = random_user.user
            random_user = data[message.chat.id].users.get(random_user.id, User(random_user, message.chat.id))

            otv = f'А потом пригляделся - {random_user.name} отдыхает. ' \
                  f'Взял, да {msg.pre_hit} {options[user.option]} ему. ' \
                  f'<tg-spoiler>{user.atack}HP</tg-spoiler>'
            random_user.hp -= user.atack
            user.weapon.durability -= 1
            otv = f'{otv}\n{random_user.tag} (💪{random_user.hp} HP)'
            if random_user.hp == 0:
                user.uebal += 1
                random_user.hp = 100
                random_user.ban_time = int(time.time()) + 2 * cfg.time_ban
                # to_ban(random_user.id, random_user.chat_id, 2 * cfg.time_ban)
                otv = f'{otv} бан тебе на {round(2 * cfg.time_ban)} секунд ☠️☠️☠️\n'
            await message.answer(otv + msg_ban, parse_mode='HTML')
            if msg_ban:
                await message.answer(msg_ban)
            user.update()
            random_user.update()
            del active_polls[poll.id]
            return

    users_list = [chat.users[_id] for _id in poll.voters]

    try:
        await smotrit.delete()
    except MessageNotModified:
        return

    msg_answer = ''
    pairs = []
    while len(users_list) > 0:
        if len(users_list) == 1:
            users_list *= 2
        random_pair = [users_list.pop(random.randrange(len(users_list))) for _ in range(2)]
        pairs.append(random_pair)

    for pair in pairs:
        user1, user2 = pair
        hit1 = f'{user1.name} {msg.pre_hit} {options[user1.option]}'
        hit2 = f'{user2.name} {msg.pre_hit} {options[user2.option]}'
        if user1.id == user2.id:
            otv = f'{hit1} сам себе <tg-spoiler>{user1.atack}HP</tg-spoiler>'
            user1.hp -= user1.atack
            user1.weapon.durability -= 1
        elif user1.option - user2.option in [-1, 2]:
            otv = f'{hit1} <tg-spoiler>{user1.atack}HP</tg-spoiler>, '
            if random.randint(1, 100) < 20 and user2.weapon.name != 'нет':
                weapon = copy.copy(user2.weapon)
                user2.weapon.durability = 0
                await weapon_drop(message, weapon)
                otv = otv + f'{user2.name} потерял оружие.'
            else:
                otv = otv + f'{user2.name} {msg.damage}'
            user2.hp -= user1.atack
            user1.weapon.durability -= 1
            if user2.hp == 0:
                user1.uebal += 1
        elif user1.option == user2.option:
            if random.randint(0, 1) == 0:
                otv = f'{hit1} <tg-spoiler>{user1.atack}HP</tg-spoiler>, '
                if random.randint(1, 100) < 20 and user2.weapon.name != 'нет':
                    weapon = copy.copy(user2.weapon)
                    user2.weapon.durability = 0
                    await weapon_drop(message, weapon)
                    otv = otv + f'{user2.name} потерял оружие.'
                else:
                    otv = otv + f'{user2.name} {msg.damage}'
                user2.hp -= user1.atack
                user1.weapon.durability -= 1
                if user2.hp == 0:
                    user1.uebal += 1
            else:
                otv = f'{hit2} <tg-spoiler>{user2.atack}HP</tg-spoiler>, '
                if random.randint(1, 100) < 20 and user1.weapon.name != 'нет':
                    weapon = copy.copy(user1.weapon)
                    user1.weapon.durability = 0
                    await weapon_drop(message, weapon)
                    otv = otv + f'{user1.name} потерял оружие.'
                else:
                    otv = otv + f'{user1.name} {msg.damage}'
                user1.hp -= user2.atack
                user2.weapon.durability -= 1
                if user1.hp == 0:
                    user2.uebal += 1
        else:
            otv = f'{hit2} <tg-spoiler>{user2.atack}HP</tg-spoiler>, '
            if random.randint(1, 100) < 20 and user1.weapon.name != 'нет':
                weapon = copy.copy(user1.weapon)
                user1.weapon.durability = 0
                await weapon_drop(message, weapon)
                otv = otv + f'{user1.name} потерял оружие.'
            else:
                otv = otv + f'{user1.name} {msg.damage}'
            user1.hp -= user2.atack
            user2.weapon.durability -= 1
            if user1.hp == 0:
                user2.uebal += 1
        msg_answer = msg_answer + otv + "\n"
        user1.update()
        user2.update()

    await message.answer(msg_answer, parse_mode='HTML')

    # users_dict = active_polls[poll.id].voters
    msg_answer = ''
    for voter_id in poll.voters:
        user = chat.users[voter_id]
        otv = f'{user.tag} (💪{user.hp} HP)'
        if user.hp == 0:
            user.hp = 100
            user.ban_time = int(time.time()) + 2 * cfg.time_ban
            user.update()
            otv = f'{otv} бан тебе на {round(2*cfg.time_ban)} секунд ☠️☠️☠️'
        msg_answer = msg_answer + otv + '\n'
    msg_answer += msg_ban
    await message.answer(msg_answer, parse_mode="HTML")

    del active_polls[poll.id]

    # res = (1200, 800)
    # pygame.init()
    # surface = pygame.Surface(res)
    # f1 = pygame.font.Font('c:/windows/fonts/Tahoma.ttf', 20)
    # kadr = 1
    # surface.fill(pygame.Color('white'))
    # image = pygame.image.load(f'alco_png/1/{random.randint(1, 5)}.png')
    # surface.blit(image, (0, 0))
    # image = pygame.image.load(f'alco_png/2/{random.randint(1, 5)}.png')
    # surface.blit(image, (0, 0))
    # image = pygame.image.load(f'alco_png/3/{random.randint(1, 5)}.png')
    # surface.blit(image, (0, 0))
    # text = f1.render(f'{name(key, message.chat.id)}', True, 'black')
    # surface.blit(text, (600 - text.get_rect().centerx, 700))
    # filename = f'gifs/1/{kadr:3}.png'
    # pygame.image.save(surface, filename)
    # kadr += 1
    # pygame.draw.rect(surface, 'white', (0, 700, 1200, 800))
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         pygame.quit()

    #     text1 = f1.render(f'{otv}', True, 'black')
    #     text_size = f1.size(f'{otv}')
    #     surface.blit(text1, (600 - text_size[0] // 2, 700))
    #     filename = f'gifs/1/{kadr:3}.png'
    #     pygame.image.save(surface, filename)
    #     kadr += 1
    # pygame.quit()


async def hit(message: types.Message):
    if message.reply_to_message.from_user.is_bot:
        await message.reply('Сам себе уеби, придурок')
        return

    elif message.from_user.id == message.reply_to_message.from_user.id:
        await message.reply('Ты чё? Решил сам себе уебать? Давай не в этом чате. Бан тебе на 2 минуты')
        user: User = data[message.chat.id].users.get(message.from_user.id, User(message.from_user, message.chat.id))
        user.ban_time = int(time.time()) + cfg.time_ban

    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Давай!", callback_data='hit - да')
        btn2 = types.InlineKeyboardButton("Пусть живёт", callback_data='hit - нет')
        btn3 = types.InlineKeyboardButton('Налить ему и себе по 100 грамм', callback_data='hit - налить')
        btn4 = types.InlineKeyboardButton('Сильно уебать', callback_data='hit - сильно уебать')
        markup.add(btn1, btn2, btn3)
        markup.add(btn4)
        await message.reply_to_message.reply("По ебалу за такие слова!", reply_markup=markup)
        try:
            await message.bot.delete_message(message.chat.id, message.message_id)
        except MessageCantBeDeleted:
            pass


async def change_uebal(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Давай!", callback_data='hit - да')
    item2 = types.InlineKeyboardButton("Конечно", callback_data='hit - да')
    item3 = types.InlineKeyboardButton('Налить ему и себе по 100 грамм', callback_data='hit - налить')
    markup.add(item1, item2, item3)
    await message.edit_text("Уебать бы тебе за такое. Может кто поможет?", reply_markup=markup)


async def handle_poll_answer(answer: types.PollAnswer):
    if answer.option_ids:
        poll = active_polls[answer.poll_id]
        user = data[poll.chat_id].users.get(answer.user.id, User(answer.user, poll.chat_id))
        if answer.user.id not in poll.voters:
            user.option = answer.option_ids[0]
            poll.voters.append(answer.user.id)


async def callback_inline_hit(call: types.CallbackQuery):

    chat_id = call.message.chat.id

    if call.from_user.id == call.message.reply_to_message.from_user.id and call.data == 'hit - нет':
        user: User = data[chat_id].users.get(call.from_user.id, User(call.from_user, chat_id))
        await change_uebal(call.message)
        await bot.send_message(
            chat_id=chat_id,
            text=f"{user.name}, не тебе решать, уебать тебе или нет 😊😊😊")
        return

    try:
        await call.message.delete()
    except MessageCantBeDeleted:
        pass

    # если нажал на кнопку автор сообщения
    if call.from_user.id == call.message.reply_to_message.from_user.id:

        user: User = data[chat_id].users.get(call.from_user.id, User(call.from_user, chat_id))

        if call.data == 'hit - да':
            user.ban_time = int(time.time()) + cfg.time_ban
            user.hp -= user.atack
            await call.message.reply_to_message.reply(
                f"{user.name} уебал сам себе. Как он только умудрился? "
                f"Бан на {cfg.time_ban} секунд и минус {user.atack} HP"
            )
            if user.hp == 0:
                user.hp = 1
                await bot.send_message(chat_id=chat_id, text='Оставлю тебе 1 HP, думай сам что с этим делать')

        elif call.data == 'hit - сильно уебать':
            user.ban_time = int(time.time()) + cfg.time_ban * 2
            user.hp -= user.atack * 2
            await call.message.reply_to_message.reply(
                f"{user.name} очень сильно уебал сам себе. Лучше бы водку пил. "
                f"Бан на {cfg.time_ban * 2} секунд и минус {user.atack * 2} HP"
            )
            if user.hp == 0:
                user.hp = 1
                await bot.send_message(chat_id=chat_id, text='Оставлю тебе 1 HP, думай сам что с этим делать')

        elif call.data == 'hit - налить':
            user.ban_time = int(time.time()) + cfg.time_ban
            user.hp -= 10
            await call.message.reply_to_message.reply(
                f"{user.name} налил себе 2 по 100. Бан ему на 2 минуты!\nМинус 10 HP, ибо нехер бухать")
            if user.hp == 0:
                user.hp = 1
                await bot.send_message(
                    chat_id=chat_id,
                    text='Батюшки, да ты сдох от алкашки. Но 1 HP я тебе оставлю')
        user.update()

    else:
        # Нажавший на кнопку
        user1: User = data[chat_id].users.get(call.from_user.id, User(call.from_user, chat_id))
        # Автор сообщения
        user2: User = data[chat_id].users.get(
            call.message.reply_to_message.from_user.id, User(call.message.reply_to_message.from_user, chat_id))

        if call.data == 'hit - да':
            if random.randint(1, 2) == 1:
                user1.weapon.durability -= 1
                user2.hp -= user1.atack

                txt = f"{user1.name} {random.choice(msg.hit_low)}. "
                otvet = text_gen.simple_generate(
                    txt+"Чтобы ",
                    temperature=1.6,
                    max_length=48,
                    length_penalty=-0.5
                )
                otvet = f"{otvet}\n{user2.name} получил минус {user1.atack} HP"
                if user2.hp == 0:
                    user2.hp = 100
                    user1.uebal += 1
                    user2.ban_time = int(time.time()) + cfg.time_ban * 0.5
                    otvet = f"{otvet} и сдох. Бан ему на {cfg.time_ban * 0.5:.0f} секунд"
                await call.message.reply_to_message.reply(otvet)

            else:
                user1.hp -= user2.atack
                user2.weapon.durability -= 1
                otvet = f"{user1.name} попытался ёбнуть тебе, но не попал! " \
                        f"{user2.name} уебал в ответ на {user2.atack} HP"
                if user1.hp == 0:
                    user1.hp = 100
                    user2.uebal += 1
                    otvet = f'{otvet}\n{user1.name}, ты сдох. Бан тебе на {cfg.time_ban * 0.5:.0f} секунд'
                    user1.ban_time = int(time.time()) + cfg.time_ban * 0.5
                await call.message.reply_to_message.reply(otvet)

        elif call.data == 'hit - нет':
            await call.message.reply_to_message.reply("Хотели вроде дать по ебалу, но передумали")

        elif call.data == 'hit - налить':
            user1.ban_time = int(time.time()) + cfg.time_ban * 0.5
            user2.ban_time = int(time.time()) + cfg.time_ban * 0.5
            await call.message.reply_to_message.reply(
                f"{user1.name} разлил по 100 грамм. "
                f"{user2.name} поддержал. И оба ушли в запой (в бан) на {cfg.time_ban * 0.5:.0f} секунд!"
                f"\nМинус 10 HP обоим. Пить вредно"
            )
            user1.hp -= 10
            if user1.hp == 0:
                user1.hp = 1
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'Батюшки, {user1.name} да ты сдох от алкашки. 1 HP у тебя теперь будет')

            user2.hp -= 10
            if user2.hp == 0:
                user2.hp = 1
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'Батюшки, {user2.name} да ты сдох от алкашки. 1 HP у тебя теперь будет')

        elif call.data == 'hit - сильно уебать':
            if random.randint(1, 4) == 1:
                user1.weapon.durability -= 2
                user2.hp -= user1.atack * 2

                otvet = f"{user1.name} очень сильно уебал за такие слова! \n" \
                        f"{user2.name} получил минус {user1.atack * 2} HP"
                if user2.hp == 0:
                    user2.hp = 100
                    user1.uebal += 1
                    user2.ban_time = int(time.time()) + cfg.time_ban
                    otvet = f'{otvet} и сдох. Бан ему на {cfg.time_ban:.0f} секунд'
                await call.message.reply_to_message.reply(otvet)
            else:
                user2.weapon.durability -= 1
                user1.hp -= user2.atack

                otvet = f"{user1.name} сильно замахнулся, но забыл нахуя! \n" \
                        f"Получил в ответ по морде, минус {user2.atack} HP"
                if user1.hp == 0:
                    user1.hp = 1
                    user1.ban_time = int(time.time()) + cfg.time_ban
                    user2.uebal += 1
                    otvet = f'{otvet}  и сдох. Но 1 HP я ему оставлю. Бан ему на {cfg.time_ban:.0f} секунд'
                await call.message.reply_to_message.reply(otvet)
        user1.update()
        user2.update()

import aiofiles
from aiogram import types, Dispatcher

from create_bot import bot
from dialogs import msg, prikol


async def to_chat(message: types.Message):
    text = message.get_args()
    await bot.send_message(chat_id=int(text.split()[0]), text=' '.join(text.split()[1:]))


async def send_welcome(message: types.Message):
    await message.answer(msg.help)
    # await message.answer(
    #     "Если что, пишите сюда [Смотрящий за ботом](tg://user?id=176814724)", parse_mode="Markdown")


async def cmd_save(message: types.Message):
    if not message.get_args():
        return
    else:
        async with aiofiles.open("prikol.txt", "a") as file:
            await file.write(message.get_args() + "\n")
        await message.reply("Пожалуй, я запомню эту хуйню")


async def cmd_op(message: types.Message):
    await message.bot.delete_message(message.chat.id, message.message_id)
    # await message.reply_to_message.reply(random.choice(msg.zaebal))
    await message.reply_to_message.reply(await prikol.random_string)


async def some_handler(my_chat_member: types.ChatMemberUpdated):
    print(my_chat_member.new_chat_member.status)
    if my_chat_member.new_chat_member.status == 'member' and my_chat_member.old_chat_member.status != 'administrator':
        print(f'Добавили в чат {my_chat_member.chat.id}')
        await bot.send_message(
            chat_id=my_chat_member.chat.id,
            text='Привет. Я умею всякое, но лучше дать мне права администратора и почитать /help'
        )
    if my_chat_member.old_chat_member.status == 'administrator':
        pass
    if my_chat_member.new_chat_member.status in ['restricted', 'left', 'banned', 'kicked']:
        print(f'Выкинули из чата {my_chat_member.chat.id}')


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_op, commands=["op"])
    dp.register_message_handler(cmd_save, commands=["save"])
    dp.register_message_handler(send_welcome, commands=["help"])
    dp.register_message_handler(to_chat, commands=["tochat"])
    dp.register_my_chat_member_handler(some_handler)

# @rate_limit(60, 'sim')
# @dp.message_handler(commands=["sim"])
# async def cmd_sim(message: types.Message):
#     if cfg.sim_gens:
#         return
#     await bot.send_poll(
#         chat_id=message.chat.id, question='Битва клеточных кланов\nВыбирай клан',
#         options=[
#             'Без бонусов (необезательный, если выбраны другие)',
#             'Хищник, способный поедать других(скорость -1)',
#             'Скорость +1 (Уменьшается время жизни)',
#             'Скорость -1 (Увеличивается время жизни)'],
#         is_anonymous=False, open_period=30, allows_multiple_answers=True
#         # type="quiz", correct_option_id=0
#     )
#     await asyncio.sleep(30)
#     cfg.sim_gens[2070208630] = {
#         'id': 2070208630,
#         'gen': random.randint(0, 1),
#         'speed': random.randint(2, 4),
#         'first_name': 'Бот Алкаш',
#         'vsego': 0
#     }
#     simulation.simulate(cfg.sim_gens)
#     # with open('gifs\\sim.gif', 'rb') as gif:
#     #     await bot.send_animation(chat_id=message.chat.id, animation=gif)
#     with open('gifs\\sim_pygame.mp4', 'rb') as video:
#         await bot.send_video(chat_id=message.chat.id, video=video)
#     otv = ''
#     for key in cfg.sim_gens:
#         otv = otv + f'{cfg.sim_gens[key]["first_name"]} - {cfg.sim_gens[key]["vsego"]}%\n'
#     await asyncio.sleep(5)
#     await message.answer(text=f'Результаты такие:\n{otv}')
#     cfg.sim_gens = {}


# @dp.poll_answer_handler()
# async def handle_poll_answer(quiz_answer: types.PollAnswer):
#     cfg.sim_gens[quiz_answer.user.id] = {
#         'id': quiz_answer.user.id,
#         'gen': 0, 'speed': 3,
#         'first_name': quiz_answer.user.first_name,
#         'vsego': 0
#     }
#     for option in quiz_answer.option_ids:
#         if option == 1:
#             cfg.sim_gens[quiz_answer.user.id]['gen'] = 1
#         if option == 2:
#             cfg.sim_gens[quiz_answer.user.id]['speed'] -= 1
#         if option == 3:
#             cfg.sim_gens[quiz_answer.user.id]['speed'] += 1


# @dp.message_handler(commands=["add"])
# async def cmd_add(message: types.Message):
#     with open("fraza.txt", "a") as fw:
#         print(message.reply_to_message.text, file=fw, sep="\n")
#     with open("fraza.txt") as file:
#         dialogs.nabor = file.read().splitlines()
#     await message.bot.delete_message(cfg.GROUP_ID, message.message_id)
#     await message.reply_to_message.reply("Пожалуй я запомню эту хуйню")


# @dp.message_handler(commands=["delete"])
# async def cmd_delete(message: types.Message):
#     if not message.reply_to_message:
#         return
#     stroka = message.reply_to_message.text
#     with open("prikol.txt", "r") as fr:
#         lines = fr.readlines()
#     with open("prikol.txt", "w") as fw:
#         for line in lines:
#             if stroka not in line:
#                 fw.write(line)
#     await message.bot.delete_message(cfg.GROUP_ID, message.message_id)
#     await message.reply_to_message.reply("Удалил")

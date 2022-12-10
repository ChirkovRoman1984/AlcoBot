from aiogram import Dispatcher

from handlers.parser.bani import cmd_banya
from handlers.parser.coub import cmd_c
from handlers.parser.memes import cmd_m, cmd_mem
from handlers.parser.pikabu import cmd_pika, cmd_pika2
from handlers.parser.porno import cmd_p


def register_parser_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_c, commands=["c"])
    dp.register_message_handler(cmd_m, commands=["m"])
    dp.register_message_handler(cmd_p, commands=["p"])
    dp.register_message_handler(cmd_mem, commands=["mem"])
    dp.register_message_handler(cmd_banya, commands=["banya"])
    dp.register_message_handler(cmd_pika2, commands=["pikabu"])
    dp.register_message_handler(cmd_pika, commands=["pika"], is_chat_admin=True)

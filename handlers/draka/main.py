from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

from handlers.draka.food import callback_inline_snack
from handlers.draka.hit import cmd_hit, handle_poll_answer, active_polls, callback_inline_hit
from handlers.draka.rename import cmd_rename
from handlers.draka.statistic import cmd_stat, cmd_stat_all
from handlers.draka.weapon import cmd_pushka, callback_weapon


def register_draka_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(callback_inline_snack, Text(startswith=['hp']))
    dp.register_message_handler(cmd_hit, commands=["hit"])
    dp.register_message_handler(cmd_rename, commands=['rename'])
    dp.register_message_handler(cmd_stat, commands=['stat'])
    dp.register_message_handler(cmd_stat_all, commands=['statall'])
    dp.register_message_handler(cmd_pushka, commands=['pushka'])
    dp.register_poll_answer_handler(handle_poll_answer, lambda poll_answer: poll_answer.poll_id in active_polls)
    dp.register_callback_query_handler(callback_inline_hit, Text(startswith=['hit']))
    dp.register_callback_query_handler(callback_weapon, Text(startswith=['weapon']))

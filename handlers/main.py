from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from magic_filter import F

from handlers.banned import register_banned_handlers
from handlers.dice import cmd_dice, callback_inline_dice
from handlers.draka import register_draka_handlers
from handlers.other import register_other_handlers
from handlers.parser import register_parser_handlers
from handlers.quiz import register_quiz_handlers
from handlers.text import get_text_messages, reply_text_messages


def register_all_handlers(dp: Dispatcher) -> None:

    handlers = (
        register_banned_handlers,
        register_parser_handlers,
        register_draka_handlers,
        register_other_handlers,
        register_quiz_handlers
    )
    for handler in handlers:
        handler(dp)

    dp.register_message_handler(cmd_dice, commands=["dice"])
    dp.register_callback_query_handler(callback_inline_dice, Text(startswith=['dice']))
    dp.register_message_handler(reply_text_messages, content_types=['text'], is_reply=True)
    dp.register_message_handler(
        get_text_messages,
        (F.content_type == 'text') & (F.text.len() > 3) & (~F.from_user.is_bot)
    )

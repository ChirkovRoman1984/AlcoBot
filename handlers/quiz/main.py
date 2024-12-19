from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text, IDFilter

from handlers.quiz.quiz import quiz_callback, input_quiz


def register_quiz_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(quiz_callback, Text(startswith=['quiz@']))
    dp.register_message_handler(input_quiz, IDFilter(user_id=176814724), content_types='poll', chat_type='private')

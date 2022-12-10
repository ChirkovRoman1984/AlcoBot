from aiogram import Dispatcher

from filters.is_user_banned import IsUserBanned


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(IsUserBanned)

from aiogram import Dispatcher

from middleware.throttling import ThrottlingMiddleware


def register_all_middleware(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())

from aiogram import types
from aiogram.dispatcher.filters import Filter

import config as cfg


class IsUserBanned(Filter):

    async def check(self, obj: types.Message | types.CallbackQuery | types.InlineQuery | types.Poll):
        if isinstance(obj, types.Message):
            if obj.chat.id in cfg.data:
                if obj.from_user.id in cfg.data[obj.chat.id].users:
                    return cfg.data[obj.chat.id].users[obj.from_user.id].banned
            # return False
        elif isinstance(obj, types.CallbackQuery):
            if obj.message.chat.id in cfg.data:
                if obj.from_user.id in cfg.data[obj.message.chat.id].users:
                    return cfg.data[obj.message.chat.id].users[obj.from_user.id].banned
            # return False
        elif isinstance(obj, types.InlineQuery):
            pass
        elif isinstance(obj, types.Poll):
            pass
        return False

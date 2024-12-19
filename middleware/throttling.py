from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from database.db import Chat

import config as cfg


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, _):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if message.chat.id not in cfg.data:
            cfg.data[message.chat.id]: Chat = Chat(message.chat.id)

        if handler:
            if handler.__name__ == 'get_text_messages':
                return
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        thr = await dispatcher.check_key(key)
        # delta = thr.delta
        # print(key, thr.exceeded_count, delta)
        if thr.exceeded_count > 1:
            limit = thr.rate - thr.delta
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # await self.message_throttled(message, t)
            if t.exceeded_count <= 2:
                print(key)
                if key in ['m', 'coub', 'p']:
                    await message.answer(f'Новые сисечки для тебя только через {round(t.rate - t.delta)} секунд')
                elif key == 'hit':
                    await message.answer(f'Отдохни после драки немного. Осталось {round(t.rate - t.delta)} секунд')
                elif key == 'dice':
                    await message.answer(f'Казино откроется через {round(t.rate - t.delta)} секунд')
                # else:
                #     await message.answer(f'Не флуди! Отдохни {round(t.rate - t.delta)} секунд')
            raise CancelHandler()

    # async def message_throttled(self, message: types.Message, throttled: Throttled):
        # handler = current_handler.get()
        # dispatcher = Dispatcher.get_current()
        # if handler:
        #     key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        # else:
        #     key = f"{self.prefix}_message"
        # delta = throttled.rate - throttled.delta
        # if throttled.exceeded_count <= 2:
            # await message.reply(f'Отдыхай еще {round(throttled.rate, 1)} секунд')
        # await asyncio.sleep(delta)
        # thr = await dispatcher.check_key(key)
        # if thr.exceeded_count == throttled.exceeded_count:
        #     await message.reply("Давай посмотрим... что ты там хотел?")

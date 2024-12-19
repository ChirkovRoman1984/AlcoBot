import asyncio
import logging
import time

from aiogram.utils.exceptions import BadRequest, ChatNotFound

import config as cfg
from filters import register_all_filters
from handlers import register_all_handlers

from create_bot import dp
from create_bot import bot
from aiogram import executor, Dispatcher
from database.db import db, Chat
from handlers.parser import pikabu
from handlers.parser.memes import getmem3
from middleware import register_all_middleware

logging.basicConfig(
        filename=f'log/{time.strftime("%Y-%m-%d", time.localtime())}.log',
        filemode='a',
        format='[{asctime}] - [{levelname}] - {message}',
        style='{',
        datefmt='%H:%M:%S',
        level=logging.INFO,
        encoding='utf-8',
    )

# root_logger = logging.getLogger()
# root_logger.setLevel(logging.INFO)
# log_file = logging.FileHandler(f'log/{time.strftime("%Y-%m-%d", time.localtime())}.log', mode='a', encoding='utf-8')
# log_file.setFormatter(logging.Formatter(fmt='[{asctime}] - [{levelname}] - {message}', style='{', datefmt='%H:%M:%S'))
# root_logger.addHandler(log_file)


async def loop_msg() -> None:

    while True:
        await asyncio.sleep(60)

        for chat_id in cfg.data:
            if chat_id == bot['config'].bot.main_group_id:
                if time.time() - cfg.data[chat_id].last_msg_time > 3600:
                    cfg.data[bot['config'].bot.main_group_id].last_msg_time = time.time()
                    mem = await getmem3()
                    try:
                        await bot.send_photo(chat_id=bot['config'].bot.main_group_id, photo=mem)
                    except BadRequest:
                        logging.info(msg=f'Ошибка при отправке мема по таймауту\n{mem}')

            if time.time() - cfg.data[chat_id].last_msg_time > cfg.data[chat_id].pikabu_delta > 0:
                cfg.data[chat_id].last_msg_time = time.time()
                try:
                    await pikabu.show(chat_id)
                except ChatNotFound:
                    print('Чат удалился', chat_id)


# async def on_startup(disp: Dispatcher) -> None:
#     """
# Регистрация всех хендлеров, запуск задачи для рассылки
#     @param disp: aiogramm Dispatcher
#     """
#     # register_all_middleware(disp)
#     # register_all_filters(disp)
#     # register_all_handlers(disp)
#
#     # chats_config = db.get_config()
#     # for chat_config in chats_config:
#     #     chat_id = chat_config[0]
#     #     cfg.data[chat_id] = Chat(chat_id)
#     #
#     # asyncio.create_task(loop_msg())


async def on_shutdown(_):
    log_msg = '\n'
    for chat in cfg.data:
        log_msg = f'{log_msg} {chat} ************\n'
        for user in list(cfg.data[chat].users.values()):
            log_msg = f'{log_msg}, {user.name}'
        log_msg += '\n'
    logging.info(msg=log_msg)


if __name__ == '__main__':

    register_all_middleware(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # bot.delete_webhook(drop_pending_updates=True)

    executor.start_polling(
        dp,
        skip_updates=True,
        # on_startup=on_startup,
        on_shutdown=on_shutdown
    )

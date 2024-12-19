from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import load_config, Config

storage = MemoryStorage()

config = load_config(".env")
bot = Bot(token=config.bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

bot['config']: Config = config

def rate_limit(limit=1, key=None):
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator

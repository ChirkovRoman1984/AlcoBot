import json
import random
import aiohttp
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted
from bs4 import BeautifulSoup

from create_bot import rate_limit
from handlers.parser.headers import headers


list_coubs = []


@rate_limit(30, 'coub')
async def cmd_c(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    gif = await get_coub()
    await message.answer_animation(gif)


async def get_coub():
    """
    Асинхронный парсинг случаной страницы 'coub.com' с девочками.
    :return: ссылка на видео (.mp4)
    """
    global list_coubs
    if not list_coubs:
        url = f'https://coub.com/api/v2/timeline/random/fashion?page={random.randint(1, 50)}'
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
            coubs_dict = json.loads(soup.get_text())
            for co in coubs_dict['coubs']:
                list_coubs.append(co['file_versions']['html5']['video']['med']['url'])

    coub = random.choice(list_coubs)
    list_coubs.remove(coub)
    return coub

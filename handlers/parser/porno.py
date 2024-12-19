import random
import time

import aiohttp
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted
from bs4 import BeautifulSoup

from handlers.parser.headers import headers
from create_bot import rate_limit, bot

list_images = []
popular_gifs = []


@rate_limit(30, 'p')
async def cmd_p(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    if time.localtime().tm_wday == 4:
        await show(message)
    else:
        mem = await get_gif()
        await message.answer("Ты чё??? Порно только по пятницам!")
        await message.answer_animation(mem)


async def show(message: types.Message):
    if message.chat.id in bot['config'].bot.trusted_groups:
        image = await get_image()
        await message.answer_animation(image)
    else:
        await message.answer('Сорян, лавочка закрылась. Можно попросить админа в личку открыть доступ')


async def get_image():
    global list_images
    if not list_images:
        url = f'https://2gifs.ru/page/{random.randint(2, 30)}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
            items = soup.find_all('img', referrerpolicy="no-referrer")
            for i in items:
                list_images.append(i['src'])

    image = random.choice(list_images)
    list_images.remove(image)
    return image


async def get_gif():
    global popular_gifs
    if not popular_gifs:
        images = []
        url = 'https://gfycat.com/ru/popular-gifs'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                if not response.ok:
                    return None
                soup = BeautifulSoup(await response.text(), 'lxml')
            items = soup.find_all('img', class_="image media")
            for i in items:
                images.append(i['src'])
        popular_gifs = images.copy()

    gif = random.choice(popular_gifs)
    popular_gifs.remove(gif)
    return gif

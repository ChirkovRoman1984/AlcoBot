# import aiofiles
import random
import json

import aiohttp
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BadRequest
from bs4 import BeautifulSoup
# from fastai.vision.all import PILImage
# from PIL import Image

import config
# from ai.girls_classifier import girl_class

from create_bot import rate_limit
from dialogs import alco_images
from handlers.parser.classes import titties
# from handlers.parser.photo_35 import photo_35
from handlers.parser.headers import headers


async def get_cat():
    """
    Парсинг 100 картинок с котиками с сайта gfycat.com
    """
    if not config.cats:
        cats_gifs = []
        url = 'https://api.gfycat.com/v1/gfycats/' \
              'search?search_text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%D0%B8&count=100&start=1'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                if not response.ok:
                    return None
                soup = BeautifulSoup(await response.text(), 'lxml')
            gifs_dict = json.loads(soup.get_text())
            for gif in gifs_dict['gfycats']:
                cats_gifs.append(gif['max5mbGif'])
            config.cats = cats_gifs.copy()
    cat_gif = random.choice(config.cats)
    config.cats.remove(cat_gif)
    return cat_gif


async def cmd_mem(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass
    # async with aiofiles.open('alco_img.txt', mode='r') as file:
    #     images = await file.read()
    #     images = images.splitlines()
    mem = await alco_images.random_string
    # mem = random.choice(images)
    if mem:
        if mem[-3:] == 'gif':
            await message.answer_animation(mem)
        else:
            await message.answer_photo(mem)
    # else:
    #     await message.answer('Сервер с девочками не отвечает')


# async def get_woman():
#     """
#     Асинхронный парсинг joyreactor.com/tag/erotic. Парсится максимальное кол-во страниц
#     и потом парсится рандомная.
#     :return: ссылка на изображение .jpg или .gif или None если сервер не отвечает
#     """
#     if not config.images_ero:
#         images = []
#         url = 'http://joyreactor.com/tag/erotic'
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url=url, headers=headers) as response:
#                 if not response.ok:
#                     return None
#                 soup = BeautifulSoup(await response.text(), 'lxml')
#
#             # Число страниц
#             a = int(soup.find('a', class_='next').get('href').split('/')[-1]) + 1
#
#             # Ссылка на рандомную страницу
#             url = f'http://joyreactor.com/tag/erotic/{random.randint(1, a)}'
#             # assert str(response.url) == url
#             async with session.get(url=url, headers=headers) as response:
#                 # if not response.ok:
#                 #     return None
#                 soup = BeautifulSoup(await response.text(), 'lxml')
#
#         items = soup.find_all('div', class_='image')
#         for item in items:
#             if item.find('a', class_='video_gif_source'):
#                 images.append(item.find('a', class_='video_gif_source').get('href'))
#             elif item.find('img'):
#                 images.append(item.find('img').get('src'))
#         config.images_ero = images.copy()
#     image = random.choice(config.images_ero)
#     config.images_ero.remove(image)
#     return image


@rate_limit(10, 'm')
async def cmd_m(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass
    # mem = await get_woman()
    mem = await titties.get_image(message)
    # mem = await photo_35.get_image(message)
    if not mem:
        await message.answer('Сервер с девочками не отвечает')
    elif mem[-3:] == 'gif':
        try:
            await message.answer_animation(mem)
        except BadRequest:
            await message.answer('Нет прав на отправку гиф анимиации в чат (((')
    else:
        await message.answer_photo(mem)
        # if message.chat.id == bot['config'].bot.main_group_id:
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url=mem) as response:
        #             if not response.ok:
        #                 pass
        #             img = PILImage.create(await response.content.read())
        #             # img = Image.create(await response.content.read())
        #     pred, pred_idx, probs = girl_class.predict(img)
        #     if probs[pred_idx] > 0.7:
        #         if pred == 'slim':
        #             await message.answer('Заебись такая девочка')
        #         elif pred == 'black':
        #             await message.answer('Люблю черненьких!')
        #         else:
        #             await message.answer('Вот это толстуха!!!')


async def getmem3():
    """
    Парсит сайт с 'котиками'
    :return: Ссылка на изображение
    """
    if not config.images_mem:
        images = []
        urls = []
        # url = 'https://www.anekdotovmir.ru/category/mjemy/'
        url = 'https://www.anekdotovmir.ru/category/kartinki/'
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
            items = soup.find_all('h2', class_="blog-entry-title entry-title")
            for item in items[:1]:
                if item.find('a').get('href'):
                    urls.append(item.find('a').get('href'))

            for url in urls:
                async with session.get(url=url, headers=headers) as response:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                items = soup.find('div', class_="entry-content clr").find_all('img', loading='lazy')
                for i in items:
                    data_src = i.get('data-src')
                    if data_src:
                        images.append(data_src[data_src.rfind('http'):])

        config.images_mem = images.copy()
    image = random.choice(config.images_mem)
    config.images_mem.remove(image)
    return image

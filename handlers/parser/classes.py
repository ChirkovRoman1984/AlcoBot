import random

import aiohttp
from aiogram import types
from aiohttp import ClientConnectorError
from bs4 import BeautifulSoup

from handlers.parser.headers import headers


class PornoGifs:
    def __init__(self):
        self.chats_images: dict = {}

    def get_gif(self, message: types.Message):
        images = self.chats_images.get(message.chat.id)
        if not images:
            pass
        gif = random.choice(images)
        images.remove(gif)
        return gif


class Titties:
    url = 'http://joyreactor.com/tag/erotic/new'
    # proxy = 'http://165.154.243.247:80'
    # Генеральная очередь: список из списков ссылок на картинки с одной страницы сайта
    queue: list = []
    # Позиция в генеральной очереди для каждого чата
    index_queue: dict = {}
    # Теккущий список картинок для каждого чата
    images: dict = {}
    num_pages = 0

    async def get_num_pages(self):
        async with aiohttp.ClientSession() as session:
            try:
                # async with session.get(url=self.url, headers=headers, proxy=self.proxy) as response:
                async with session.get(url=self.url, headers=headers) as response:
                    if not response.ok:
                        return 1
                    soup = BeautifulSoup(await response.text(), 'lxml')
                    # Число страниц
                    n_pages = int(soup.find('a', class_='w-5/12').get('href').split('/')[-1]) + 1
            except ClientConnectorError:
                return 0
        return n_pages

    async def get_new_images(self):
        images = []
        # Ссылка на рандомную страницу. Счёт на ресурсе идёт с конца. Последняя по номеру стр - первая на ресурсе
        url = self.url + f'/{self.num_pages - round(random.gammavariate(3., 2.))}'
        async with aiohttp.ClientSession() as session:
            try:
                # async with session.get(url=url, headers=headers, proxy=self.proxy) as response:
                async with session.get(url=url, headers=headers) as response:
                    if response.ok:
                        soup = BeautifulSoup(await response.text(), 'lxml')
                        items = soup.find_all('div', class_='image')
                        for item in items:
                            if item.find('a', class_='video_gif_source'):
                                images.append(item.find('a', class_='video_gif_source').get('href'))
                            elif item.find('img'):
                                images.append(item.find('img').get('src'))
            except ClientConnectorError:
                pass
        return images

    async def get_image(self, message: types.Message):
        # 1. Берем список фоток из общего словаря для всех чатов
        images = self.images.get(message.chat.id, [])
        # 2. Если списка нет, значит надо взять новый по индексу для этого чата, индекс + 1
        if not images:
            index = self.index_queue.get(message.chat.id, -1)
            # 3. Если индекса нет, то значит не было еще запросов. Берем нулевой индекс
            if index == -1:
                self.index_queue[message.chat.id] = 0
                index = 0
            # 4. Если индекс больше длинны списка всех фоток, то надо напарсить еще
            if index >= len(self.queue):
                if self.num_pages == 0:
                    self.num_pages = await self.get_num_pages()
                    if self.num_pages == 0:
                        return None
                new_images = await self.get_new_images()
                if not new_images:
                    return None
                self.queue.append(new_images)

            self.images[message.chat.id] = self.queue[index].copy()
            images = self.images.get(message.chat.id)
            self.index_queue[message.chat.id] += 1

        image = random.choice(images)
        images.remove(image)
        return image


titties = Titties()

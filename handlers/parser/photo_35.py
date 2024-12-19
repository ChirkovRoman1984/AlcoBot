import random

import aiohttp
from aiogram import types
from aiohttp import ClientConnectorError
from bs4 import BeautifulSoup

from handlers.parser.headers import headers


class Photo35:
    # url = 'https://35photo.pro/genre_97/'
    url = 'https://35photo.pro/genre_97/new/'
    last_id = ''
    # Генеральная очередь: список из списков ссылок на картинки с одной страницы сайта
    queue: list = []
    # Позиция в генеральной очереди для каждого чата
    index_queue: dict = {}
    # Теккущий список картинок для каждого чата
    images: dict = {}

    @property
    def php_request(self):
        return f'/show_block.php?type=getNextPageData&page=genre&lastId={self.last_id}&community_id=97&photo_rating=0'
        # return f'/show_block.php?type=getNextPageData&page=genre&lastId={self.last_id}&community_id=97&photo_rating=35'

    async def first_page(self):
        img_urls = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=self.url, headers=headers) as response:
                    if response.ok:
                        soup = BeautifulSoup(await response.text(), 'lxml')
                        items = soup.find_all('img', class_="showPrevPhoto")
                        for item in items:
                            img_urls.append(item.get('data-src'))
                        self.last_id = img_urls[-1].split('/')[-1].split('_')[0]
            except ClientConnectorError:
                pass
        return img_urls

    async def initiate(self):
        images = await self.first_page()
        self.queue.append(images)

    async def get_new_images(self):
        img_urls = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=self.php_request, headers=headers) as response:
                    if response.ok:
                        soup = BeautifulSoup(await response.text(), 'lxml')
                        items = soup.find_all('img', class_='\\"showPrevPhoto\\"')
                        for item in items:
                            img_urls.append(item.get('src')[2:-2])
                        self.last_id = img_urls[-1].split('/')[-1].split('_')[0]
            except ClientConnectorError:
                return None
        return img_urls

    async def get_image(self, message: types.Message):
        if not self.last_id:
            await self.initiate()
        # 1. Берем список фоток из общего словаря для всех чатов
        images = self.images.get(message.chat.id, [])
        # 2. Если список пустой, значит надо взять новый по индексу для этого чата, индекс + 1
        if not images:
            index = self.index_queue.get(message.chat.id, -1)
            # 3. Если индекса нет, то значит не было еще запросов. Берем нулевой индекс
            if index == -1:
                self.index_queue[message.chat.id] = 0
                index = 0
            # 4. Если индекс больше длинны списка всех фоток, то надо напарсить еще
            if index >= len(self.queue):
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


photo_35 = Photo35()

import time

import aiohttp
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted
from bs4 import BeautifulSoup

import config as cfg
from database.db import Chat
from handlers.parser.headers import headers
from create_bot import bot

list_pikabu_stories = []


async def cmd_pika(message: types.Message):
    if not message.get_args():
        return
    try:
        delta = abs(int(float(message.get_args()) * 3600))
    except ValueError:
        await message.answer('Аргумент функции должен быть численным (в часах)')
        return

    if delta == 0:
        await message.answer('Больше не буду постить приколы с пикабу')

    else:
        await message.answer(
            f'Буду слать вам приколы с пикабу, если будите молчать больше {round(delta/3600, 1)} часов')
        if message.chat.id not in cfg.data:
            cfg.data[message.chat.id] = Chat(message.chat.id)
        cfg.data[message.chat.id].last_msg_time = int(time.time())

    cfg.data[message.chat.id].pikabu_delta = delta
    cfg.data[message.chat.id].db_config_update()


async def cmd_pika2(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass

    await show(message.chat.id)


async def show(chat_id):
    stories = cfg.data[chat_id].pikabu_to_post
    if not stories:
        stories = await get_stories(chat_id)
    story = stories[0]
    cfg.data[chat_id].pikabu_to_post.remove(story)
    cfg.data[chat_id].pikabu_posted.insert(0, story['link'])

    text = story['title'] + story['text'] if 'text' in story else story['title']

    await bot.send_message(chat_id=chat_id, text=text)
    if 'imgs' in story:
        if len(story['imgs']) > 1:
            media = types.MediaGroup()
            for image in story['imgs']:
                media.attach_photo(image)
            await bot.send_media_group(chat_id=chat_id, media=media)
        else:
            await bot.send_photo(chat_id=chat_id, photo=story['imgs'][0])
    # db.update_config2(chat_id)
    cfg.data[chat_id].db_config_update()


async def get_pikabu():
    """
    Асинхронный парсинг главной страницы пикабу
    @return: Список из словарей (историй с пикабу)
    """
    list_stories = []
    # url = f'https://pikabu.ru/?twitmode=1&of=v2'
    url = f'https://pikabu.ru/best?twitmode=1&of=v2'
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        if response.ok:
            soup = BeautifulSoup(await response.text(), 'lxml')
            stories = soup.find_all('div', class_="story__main")
            for item in stories:
                story = {}
                story_texts = item.find_all('div', class_="story-block story-block_type_text")
                story_imgs = item.find_all('img', class_="story-image__image")
                story_title = item.find('a', class_="story__title-link")
                images = []
                if story_title:
                    if '?from=cpm' in story_title.get('href'):
                        continue
                    story['link'] = story_title.get('href')
                    story['title'] = story_title.getText() + '\n'

                    if story_texts:
                        text = ''
                        for story_text in story_texts:
                            text += story_text.getText()
                        story['text'] = text

                for img in story_imgs:
                    images.append(img.get('data-large-image'))
                if images:
                    story['imgs'] = images
                if any(i in story for i in ('text', 'imgs')):
                    list_stories.append(story)
    return list_stories


async def get_stories(chat_id):
    """
    Сравнение списка готовых историй и опбликованных в чате
    @return: Список историй готовых для публикации в конкретном чате
    """
    list_stories = await get_pikabu()
    if not list_stories:
        return []

    pikabu_posted = cfg.data[chat_id].pikabu_posted
    # if not pikabu_posted:
    #     config.data[chat_id].pikabu_to_post = list_stories
    # else:
    for story in list_stories:
        if story['link'] not in pikabu_posted:
            cfg.data[chat_id].pikabu_to_post.append(story)
    return cfg.data[chat_id].pikabu_to_post

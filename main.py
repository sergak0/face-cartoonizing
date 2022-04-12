import os
import random
import threading
import urllib

import cv2
import numpy as np
import pandas as pd
from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from config import BOT_TOKEN, PROJECT_DIR
from worker import Worker, get_image_path

from dash import Dash
from dashboard import serve_layout
import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
worker = Worker()
app = Dash(__name__)
app.layout = serve_layout
data = pd.read_csv('dashboard_data.csv')


async def download_file(file_id, document_id):
    file_info = await bot.get_file(document_id)
    filename, file_extension = os.path.splitext(file_info.file_path)
    image_name = file_id + file_extension
    image_path = os.path.join(PROJECT_DIR, 'photos', image_name)
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}', image_path)
    return image_name


async def send_image(image, chat_id, markup=None):
    id = random.randint(0, 1e9)
    path = 'image_{}.jpg'.format(id)
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    with open(path, 'rb') as f:
        await bot.send_photo(
            chat_id=chat_id,
            photo=f,
            reply_markup=markup
        )
    os.remove(path)


@dp.message_handler(commands=['start', 'help'])
async def some_handler(message: types.Message):
    start_message = 'Привет! Это бот, который умеет преобразовывать фотографии лиц в мультяшные. \n' \
                    'Просто пришли нам свою фотку, и перерисуем ее в мультяшный стиль'
    await message.answer(start_message)


@dp.message_handler(content_types=['photo'], state='*')
async def handle_docs_photo(message: types.Message):
    document_id = message['photo'][-1].file_id
    file_id = message['photo'][-1].file_unique_id
    image_name = await download_file(file_id, document_id)

    # task_queue.put((image_name, message.chat.id, None, True))
    await message.answer('Ищем лица на вашем фото... \n')
    faces = worker.crop_faces(image_name)

    if not faces:
        await message.answer('Не смогли найти ни одного лица, попробуйте отправить другую фотографию')
        return None

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton('Обработать чуть-чуть', callback_data='do|merged'),
        InlineKeyboardButton('Обработать сильно', callback_data='do|cartoon'),
    )

    for face in faces:
        image = np.array(face)
        await send_image(image, message.chat.id, markup)


@dp.callback_query_handler(lambda x: x.data.startswith('do'), state='*')
async def inline_go_disney_answer_callback_handler1(query: types.CallbackQuery):
    mode = query.data.split('|')[1]

    global data
    user_id = query.message.chat.id
    data = pd.concat([data, pd.DataFrame([{'time': datetime.datetime.now().date(), 'user_id': user_id}])], axis=0)
    data.to_csv('dashboard_data.csv', index=False)
    need_sent_notice = (data['user_id'] == user_id).sum() % 10 == 0

    document_id = query.message['photo'][-1].file_id
    file_id = query.message['photo'][-1].file_unique_id
    image_name = await download_file(file_id, document_id)
    path = get_image_path(image_name)
    image = worker.load_image(path)
    image = worker.predict(image, mode)

    os.remove(path)
    await send_image(image, query.message.chat.id)

    if need_sent_notice:
        await query.message.answer('Отлично, очередные 10 фото были обработаны!\n'
                                   'Поддежрать проект можно здесь - https://www.tinkoff.ru/cf/50xgBwSX8wN')

if __name__ == '__main__':
    threading.Thread(target=app.run_server, kwargs={'host': '0.0.0.0', 'port': 1919}, daemon=True).start()
    executor.start_polling(dp)


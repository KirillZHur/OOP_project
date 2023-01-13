from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import os

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

async def on_startup(_):
    print('Бот вышел в онлайн')
# Клиентская часть
@dp.message_handler(commands=['start', 'help'])
async def command_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Доброго дня')
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему: \nhttps://t.me/Image_detectionBot')

@dp.message_handler(commands=['image'])
async def command_image(message : types.Message):
    await message.answer('Загрузите изображение')
# Админ часть

# Общая часть
@dp.message_handler()
async def echo_send(message : types.Message):
    if message.text == 'Привет':
        await message.answer('И тебе привет!')

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
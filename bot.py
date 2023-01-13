from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import os, cv2
import numpy as np

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

@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)
# Админ часть

# Общая часть
@dp.message_handler()
async def echo_send(message : types.Message):
    config_path = "cfg/yolov3.cfg"
    weights_path = "weights/yolov3.weights"

    labels = open("data/coco.names").read().strip().split("\n")
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

    path_name = message
    image = cv2.imread(path_name)
    file_name = os.path.basename(path_name)
    filename, ext = file_name.split(".")

    h, w = image.shape[:2]
    # создать 4D blob
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

    # устанавливает blob как вход сети
    net.setInput(blob)
    # получаем имена всех слоев
    ln = net.getLayerNames()
    try:
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    except IndexError:
        # in case getUnconnectedOutLayers() returns 1D array when CUDA isn't available
        ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    # прямая связь (вывод) и получение выхода сети
    # измерение времени для обработки в секундах
    layer_outputs = net.forward(ln)

    font_scale = 1
    thickness = 1
    boxes, confidences, class_ids = [], [], []
    # перебираем каждый из выходов слоя
    for output in layer_outputs:
        # перебираем каждое обнаружение объекта
        for detection in output:
            # извлекаем идентификатор класса (метку) и достоверность (как вероятность)
            # обнаружение текущего объекта
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            # отбросьте слабые прогнозы, убедившись, что обнаруженные
            # вероятность больше минимальной вероятности
            if confidence > CONFIDENCE:
                # масштабируем координаты ограничивающего прямоугольника относительно
                # размер изображения, учитывая, что YOLO на самом деле
                # возвращает центральные координаты (x, y) ограничивающего
                # поля, за которым следуют ширина и высота поля
                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")
                # используем центральные координаты (x, y) для получения вершины и
                # и левый угол ограничительной рамки
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # обновить наш список координат ограничивающего прямоугольника, достоверности,
                # и идентификаторы класса
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # перебираем сохраняемые индексы
    for i in range(len(boxes)):
        # извлекаем координаты ограничивающего прямоугольника
        x, y = boxes[i][0], boxes[i][1]
        w, h = boxes[i][2], boxes[i][3]
        # рисуем прямоугольник ограничивающей рамки и подписываем на изображении
        color = [int(c) for c in colors[class_ids[i]]]
        cv2.rectangle(image, (x, y), (x + w, y + h), color=color, thickness=thickness)
        text = f"{labels[class_ids[i]]}: {confidences[i]:.2f}"
        # вычисляем ширину и высоту текста, чтобы рисовать прозрачные поля в качестве фона текста
        (text_width, text_height) = \
        cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)[0]
        text_offset_x = x
        text_offset_y = y - 5
        box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width + 2, text_offset_y - text_height))
        overlay = image.copy()
        cv2.rectangle(overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)
        # добавить непрозрачность (прозрачность поля)
        image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
        # теперь поместите текст (метка: доверие%)
        cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale, color=(0, 0, 0), thickness=thickness)

    #cv2.imwrite(filename + "_yolo3." + ext, image)
    await bot.send_photo(chat_id=message.chat.id, photo=image)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
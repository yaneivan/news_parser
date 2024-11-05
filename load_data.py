import json
import logging
import colorlog

# Создаем форматтер с цветовыми кодами
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'blue',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Создаем обработчик для вывода в консоль
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Создаем логгер и добавляем обработчик
logger = logging.getLogger('news logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def load_texts(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    texts = []

    for i in (data['messages']):
        i = i['text']
        message = ''
        for q in i:
            if type(q) == str:
                message += q
            if type(q) == dict:
                message += q['text']
        message = message.strip()
        if message:
            logger.debug(message)
            texts.append(message)
    return texts

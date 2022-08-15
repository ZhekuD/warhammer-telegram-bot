import os
import datetime
from random import choice

import aiohttp
from aiohttp import web


BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
BOT_URL = 'https://api.telegram.org/bot' + BOT_TOKEN
CHAT_ID = os.getenv('TG_CHAT_ID')

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text="I am bot")

@routes.post('/api/postMessage')
async def send_message_endpoint(request):
    await send_telegram_message()
    return web.Response(status=200)

@routes.post('/api/postPoll')
async def send_message_endpoint(request):
    resp_json = await send_telegram_poll()
    await pin_telegram_message(resp_json['result']['message_id'])
    return web.Response(status=200)

async def send_telegram_message():
    message = generate_random_message()
    params = {'chat_id': CHAT_ID, 'text': message}
    async with aiohttp.ClientSession() as session:
        async with session.post(BOT_URL + '/sendMessage',
                                params=params) as resp:
            print(resp.status)
            print(await resp.text())

async def send_telegram_poll():
    saturday = datetime.datetime.now() + datetime.timedelta(days = 5)
    sunday = saturday + datetime.timedelta(days = 1)
    question = "Хочу грати {}.{} - {}.{}!".format(
        saturday.day,
        saturday.month if saturday.month > 9 else f'0{saturday.month}',
        sunday.day,
        sunday.month if sunday.month > 9 else f'0{sunday.month}',
    )
    json = {
        "chat_id": CHAT_ID,
        "question": question,
        "options": [
            "Хочу в суботу з 13:00!",
            "Хочу в суботу з 16:00!",
            "Хочу в неділю з 13:00!",
            "Хочу в неділю з 16:00!",
            "Хочу в будні!",
            "Цікаво хто прийде..."
        ],
        "is_anonymous": False,
        "allows_multiple_answers": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(BOT_URL +  '/sendPoll',
                                json=json) as resp:
            json = await resp.json()
            return json

async def pin_telegram_message(message_id):
    json = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(BOT_URL +  '/pinChatMessage',
                                json=json) as resp:
            json = await resp.json()
            return json

def generate_random_message() -> str:
    message_list = []
    for k in range(4):
        message_line_list = []
        for i in range(4):
            bites_array = [choice(['0', '1']) for _ in range(8)]
            message_line_list.append(''.join(bites_array))
        message_list.append(' '.join(message_line_list))
    message = '\n'.join(message_list)
    return message


app = web.Application()
app.add_routes(routes)
web.run_app(app)

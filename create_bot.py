from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

storage = MemoryStorage()

TOKEN = "TOKEN"

bot = Bot(token=(f'{TOKEN}'))
dp = Dispatcher(bot, storage=storage)

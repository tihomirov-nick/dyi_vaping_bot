from aiogram import types
from aiogram.utils import executor

from create_bot import dp
from database import db
from handlers import admin
from handlers import client


async def on_startup(dp):
    db.sql_start()
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота")])


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

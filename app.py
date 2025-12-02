import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from user_private import user_private_router
from db import create_tables

load_dotenv(find_dotenv())

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_routers(user_private_router)

ALLOWED_UPDATES = ['message', 'edited_message']


async def main():
    create_tables()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

try:
    asyncio.run(main())
finally:
    bot.session.close()

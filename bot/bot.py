import asyncio
import logging

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.config import settings
from aiogram import Bot, Dispatcher
from handlers import get_all_routers

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def main():
    for router in get_all_routers():
        dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
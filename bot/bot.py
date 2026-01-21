import asyncio
import logging

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.config import settings

from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет {message.from_user.first_name}!")

# @dp.message(Command("get_video_bingx"))
# async def get_photo(message: Message):
#     current_dir = Path(__file__).parent
#     video_path = current_dir / "videos" / "bingx.mp4"

#     if not video_path.exists():
#         await message.answer("Видео не найдено")
    
#     try:
#         video = FSInputFile(video_path)
#         await message.answer_video(
#             video=video,
#             caption="Вот инструкция для подключение API из биржи BingX"
#         )
#     except Exception as e:
#         await message.answer(f"Ошибка при отправке видео {e}")

@dp.message(Command("help"))
async def get_help(message : Message):
    await message.answer("Это команда /help")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
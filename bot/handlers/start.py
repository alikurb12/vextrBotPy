from bot.bot import dp
from aiogram.filters import CommandStart
from aiogram.types import Message

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет!")
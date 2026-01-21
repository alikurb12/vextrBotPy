from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))
async def get_help(message : Message):
    await message.answer("Это команда /help")
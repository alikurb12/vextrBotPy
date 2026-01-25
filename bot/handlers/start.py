from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.models.users.dao import UsersDAO

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    existing_user = await UsersDAO.get_by_id(message.from_user.id)
    if existing_user:
        await message.answer(f"Привет. C возвращением {message.from_user.first_name}!") 
    else:
        await UsersDAO.add_or_update(
        user_id = message.from_user.id,
        username = message.from_user.username,
        chat_id = abs(message.chat.id)
        )
        await message.answer("Вы успешно зарегестрированы!")
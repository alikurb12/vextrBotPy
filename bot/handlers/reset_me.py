from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.models.users.dao import UsersDAO

router = Router()

@router.message(Command("reset_me"))
async def cmd_reset_user(message : Message):
    await UsersDAO.delete(user_id=message.from_user.id)
    await message.answer("Данные успешно удалены нажмите на /start чтобы зарегестрироватся заново")
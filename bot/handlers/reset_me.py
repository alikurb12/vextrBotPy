from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.models.users.dao import UsersDAO
import keyboards.keyboards as kb

router = Router()

@router.callback_query(F.data == 'reset_api')
async def cmd_reset_user(callback_query: CallbackQuery):
    await UsersDAO.delete(user_id=callback_query.from_user.id)
    await callback_query.message.answer(
        "Данные успешно удалены нажмите на кнопку 'Регистрация' чтобы зарегестрироватся заново", 
        reply_markup=kb.reset_api_keyboard
    )
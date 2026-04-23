from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from database.models.users.dao import UsersDAO

router = Router()

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback_query: CallbackQuery):
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    is_active = user_data.is_active if user_data and user_data.is_active is not None else True
    await callback_query.message.edit_text(
        "Вы в главном меню. Пожалуйста, выберите действие:", 
        reply_markup=kb.get_main_menu_kb(is_active=is_active)
    )

@router.callback_query(F.data == "main_menu_after_signal")
async def show_main_menu_after_signal(callback_query: CallbackQuery):
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    is_active = user_data.is_active if user_data and user_data.is_active is not None else True
    await callback_query.message.answer(
        "Вы в главном меню. Пожалуйста, выберите действие:", 
        reply_markup=kb.get_main_menu_kb(is_active=is_active)
    )

from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb

router = Router()

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Вы в главном меню. Пожалуйста, выберите действие:", 
        reply_markup=kb.main_menu_keyboard
    )

@router.callback_query(F.data == "main_menu_after_signal")
async def show_main_menu_after_signal(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Вы в главном меню. Пожалуйста, выберите действие:", 
        reply_markup=kb.main_menu_keyboard
    )
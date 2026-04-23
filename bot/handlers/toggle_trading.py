from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models.users.dao import UsersDAO
import keyboards.keyboards as kb

router = Router()

@router.callback_query(F.data == "toggle_trading")
async def toggle_trading(callback_query: CallbackQuery):
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    
    if not user_data:
        await callback_query.answer("Пользователь не найден", show_alert=True)
        return

    new_status = not user_data.is_active
    await UsersDAO.add_or_update(
        user_id=user_data.user_id,
        is_active=new_status
    )

    if new_status:
        await callback_query.answer("✅ Торговля возобновлена!", show_alert=True)
    else:
        await callback_query.answer("⏸ Торговля приостановлена!", show_alert=True)

    await callback_query.message.edit_reply_markup(
        reply_markup=kb.get_main_menu_kb(is_active=new_status)
    )

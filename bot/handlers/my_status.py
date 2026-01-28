from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from database.models.users.dao import UsersDAO

router = Router()

@router.callback_query(F.data == "my_status")
async def show_my_status(callback_query: CallbackQuery):
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    if user_data.subscription_type == "refferal":
        await callback_query.message.edit_text(
            text="Ваш тип подписки: Реферальная\n"
                 f"Дата окончания подписки: {user_data.subscription_end}\n"
                 f"Реферальный UUID: {user_data.refferal_uuid}",
            reply_markup=kb.my_status_kb 
        )
    elif user_data.subscription_type == "standard":
        await callback_query.message.edit_text(
            text="Ваш тип подписки: Платная\n"
                 f"Дата окончания подписки: {user_data.subscription_end}\n",
            reply_markup=kb.my_status_kb
        )
    else:
        await callback_query.message.edit_text(
            text="У вас нет активной подписки.",
            reply_markup=kb.my_status_kb
        )

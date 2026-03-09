from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from database.models.users.dao import UsersDAO
from backend.exchange_apis.bingx.services.get_balance import get_balance as get_balance_bingx
from backend.exchange_apis.okx.services.get_balance import get_balance as get_balance_okx

router = Router()

@router.callback_query(F.data == "my_status")
async def show_my_status(callback_query: CallbackQuery):
    
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    date_str = user_data.subscription_end.strftime('%d.%m.%Y')
    if user_data.subscription_type == "refferal":
        await callback_query.message.edit_text(
            text="Ваш тип подписки: <b>Реферальная</b>\n"
                 f"Дата окончания подписки: {date_str}\n"
                 f"Реферальный UUID: {user_data.refferal_uuid}\n"
                 f'''Ваш баланс:{await get_balance_bingx(api_key=user_data.api_key, secret_key=user_data.secret_key) 
                                if user_data.exchange == 'bingx' 
                                else await get_balance_okx(api_key=user_data.api_key, secret_key=user_data.secret_key, passphrase=user_data.passphrase)} USDT\n''',
            reply_markup=kb.my_status_kb,
            parse_mode="HTML"
        )
    
    elif user_data.subscription_type == "standard":
        await callback_query.message.edit_text(
            text="Ваш тип подписки: <b>Платная</b>\n"
                f"Дата окончания подписки: {date_str}\n"
                f'''Ваш баланс:{await get_balance_bingx(api_key=user_data.api_key, secret_key=user_data.secret_key) 
                                if user_data.exchange == 'bingx' 
                                else await get_balance_okx(api_key=user_data.api_key, secret_key=user_data.secret_key, passphrase=user_data.passphrase)} USDT\n''',
            reply_markup=kb.my_status_kb,
            parse_mode="HTML"
        )
    
    else:
        await callback_query.message.edit_text(
            text="У вас нет активной подписки.",
            reply_markup=kb.my_status_kb
        )

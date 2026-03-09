from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from database.models.users.dao import UsersDAO
from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions as get_open_positions_bingx
from backend.exchange_apis.okx.services.get_open_positions import get_open_positions as get_open_positions_okx

router = Router()

@router.callback_query(F.data == "get_my_positions")
async def show_main_menu(callback_query: CallbackQuery):
    user_data = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    if not user_data.api_key or not user_data.secret_key:
        await callback_query.message.edit_text(
            "У вас не настроены API ключи. Пожалуйста, настройте их в разделе '🔑 Сбросить API ключи'.",
            reply_markup=kb.main_menu_keyboard
        )   
        return
    if user_data.exchange == 'bingx':
        positions = await get_open_positions_bingx(api_key=user_data.api_key, secret_key=user_data.secret_key)
        if not positions:
            await callback_query.message.edit_text(
                    "У вас нет открытых позиций.",
                    reply_markup=kb.main_menu_keyboard
                )
            return
        positions_text = "\n\n".join(
            [f"📈 <b>{pos['symbol']}</b>\n"
                f"Тип: {pos['positionSide']}\n"
                f"Количество: {pos['positionAmt']}\n"
                f"Цена входа: {pos['avgPrice']}\n"
            for pos in positions]
        )
        await callback_query.message.edit_text(
            f"Ваши открытые позиции:\n\n{positions_text}",
            reply_markup=kb.main_menu_keyboard,
            parse_mode="HTML"
        )
    elif user_data.exchange == 'OKX':
        positions = await get_open_positions_okx(api_key=user_data.api_key, secret_key=user_data.secret_key, passphrase=user_data.passphrase)
        if not positions:
            await callback_query.message.edit_text(
                    "У вас нет открытых позиций.",
                    reply_markup=kb.main_menu_keyboard
                )
            return
        positions_text = "\n\n".join(
            [f"📈 <b>{pos['instId']}</b>\n"
            f"Тип: {pos['posSide']}\n"
            f"Количество: {pos['pos']}\n"
            f"Цена входа: {pos['avgPx']}\n"
            for pos in positions]
        )
        await callback_query.message.edit_text(
            f"Ваши открытые позиции:\n\n{positions_text}",
            reply_markup=kb.main_menu_keyboard,
            parse_mode="HTML"
        )


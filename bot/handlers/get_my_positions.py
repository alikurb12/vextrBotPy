from aiogram import Router, F
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from database.models.users.dao import UsersDAO
from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions

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
    try:
        positions = await get_open_positions(user_data.api_key, user_data.secret_key)
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
    except Exception as e:
        await callback_query.message.edit_text(
            f"Ошибка при получении открытых позиций: {e}",
            reply_markup=kb.main_menu_keyboard
        )
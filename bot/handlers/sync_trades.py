from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models.users.dao import UsersDAO
from backend.services.sync_trades import sync_trades_for_user

router = Router()

@router.callback_query(F.data == "sync_trades")
async def sync_trades_handler(callback_query: CallbackQuery):
    await callback_query.answer()

    user = await UsersDAO.get_by_id(user_id=callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("❌ Пользователь не найден")
        return

    if not user.api_key or not user.secret_key:
        await callback_query.message.answer("❌ API ключи не настроены")
        return

    await callback_query.message.answer("🔄 Синхронизирую позиции с биржей...")
    await sync_trades_for_user(user)
    await callback_query.message.answer(
        "✅ Синхронизация завершена!\n"
        "Позиции которых нет на бирже — закрыты в БД."
    )

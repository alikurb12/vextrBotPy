from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data.startswith("approve:"))
async def approve_request(callback_query: CallbackQuery, bot: Bot):
    data_parts = callback_query.data.split(":")
    if len(data_parts) != 4:
        await callback_query.answer("❌ Ошибка формата данных")
        return
    
    user_id = int(data_parts[1])
    chat_id = int(data_parts[2])
    refferal_uuid = data_parts[3]
    
    try:
        await callback_query.message.edit_text(
            f"✅ ЗАПРОС ОДОБРЕН\n\n"
            f"{callback_query.message.text}\n\n"
            f"👮 Модератор: {callback_query.from_user.username or callback_query.from_user.first_name}\n"
            f"✅ Статус: Одобрено",
            parse_mode="HTML",
            reply_markup=None
        )
        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ Ваш реферальный UUID одобрен!\n"
                 "Теперь вы можете продолжить регистрацию. Введите ваш API ключ:"
        )
        
        await callback_query.answer("✅ Запрос одобрен")
        
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {str(e)[:50]}")
        print(f"Ошибка при одобрении: {e}")

@router.callback_query(F.data.startswith("reject:"))
async def reject_request(callback_query: CallbackQuery, bot: Bot):
    data_parts = callback_query.data.split(":")
    
    if len(data_parts) != 4:
        await callback_query.answer("❌ Ошибка формата данных")
        return
    
    user_id = int(data_parts[1])
    chat_id = int(data_parts[2])
    refferal_uuid = data_parts[3]
    
    try:
        await callback_query.message.edit_text(
            f"❌ ЗАПРОС ОТКЛОНЕН\n\n"
            f"{callback_query.message.text}\n\n"
            f"👮 Модератор: {callback_query.from_user.username or callback_query.from_user.first_name}\n"
            f"❌ Статус: Отклонено",
            parse_mode="HTML",
            reply_markup=None
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=f"❌ Ваш реферальный UUID `{refferal_uuid}` отклонен.\n"
                 "Пожалуйста, свяжитесь с поддержкой для получения дополнительной информации."
        )
        
        await callback_query.answer("❌ Запрос отклонен")
        
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {str(e)[:50]}")
        print(f"Ошибка при отклонении: {e}")
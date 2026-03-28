from aiogram import Bot
from config.config import settings
from database.models.users.dao import UsersDAO
from bot.keyboards import keyboards as kb

async def notify_users_position_opened(symbol: str, side: str, entry_price: float, stop_loss: float, take_profit_1: float, take_profit_2: float, take_profit_3: float):
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        users = await UsersDAO.get_all()
        if not users:
            return

        side_emoji = "🟢 LONG" if side == "BUY" else "🔴 SHORT"
        message = (
            f"📈 <b>Открыта новая сделка</b>\n\n"
            f"Пара: <b>{symbol}</b>\n"
            f"Направление: <b>{side_emoji}</b>\n"
            f"Цена входа: <b>{entry_price}</b>\n"
            f"Стоп-лосс: <b>{stop_loss}</b>\n"
            f"Тейк-профит 1: <b>{take_profit_1}</b>\n"
            f"Тейк-профит 2: <b>{take_profit_2}</b>\n"
            f"Тейк-профит 3: <b>{take_profit_3}</b>\n"
        )

        for user in users:
            if user.chat_id:
                try:
                    await bot.send_message(
                        chat_id=user.chat_id,
                        text=message,
                        parse_mode="HTML",
                        reply_markup=kb.my_status_kb_after_signal
                    )
                except Exception as e:
                    print(f"Ошибка отправки уведомления пользователю id='{user.user_id}': {e}")
    finally:
        await bot.session.close()


async def notify_users_sl_moved_to_breakeven(symbol: str):
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        users = await UsersDAO.get_all()
        if not users:
            return

        message = (
            f"🔔 <b>Стоп-лосс перенесён в безубыток</b>\n\n"
            f"Пара: <b>{symbol}</b>\n"
        )

        for user in users:
            if user.chat_id:
                try:
                    await bot.send_message(
                        chat_id=user.chat_id,
                        text=message,
                        parse_mode="HTML",
                        reply_markup=kb.my_status_kb_after_signal
                    )
                except Exception as e:
                    print(f"Ошибка отправки уведомления пользователю id='{user.user_id}': {e}")
    finally:
        await bot.session.close()
import asyncio
import logging
from celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name="process_signal", bind=True, max_retries=3)
def process_signal(self, action: str, symbol: str, price: float,
                   stop_loss: float, take_profit_1: float,
                   take_profit_2: float, take_profit_3: float):
    try:
        logger.info(f"⚙️ Обработка сигнала: {action} {symbol}")
        asyncio.run(_process_signal_async(
            action=action, symbol=symbol, price=price,
            stop_loss=stop_loss, take_profit_1=take_profit_1,
            take_profit_2=take_profit_2, take_profit_3=take_profit_3,
        ))
        logger.info(f"✅ Сигнал обработан: {action} {symbol}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise self.retry(exc=e, countdown=5)

async def _process_signal_async(action, symbol, price, stop_loss,
                                 take_profit_1, take_profit_2, take_profit_3):
    from backend.exchange_apis.bingx.router import open_position_for_users_bingx
    from backend.exchange_apis.okx.router import open_position_for_users_okx
    from backend.utils.send_notification import notify_users_position_opened
    from backend.exchange_apis.bingx.router import move_sl_to_breakeven_for_all_users
    from backend.utils.send_notification import notify_users_sl_moved_to_breakeven

    if action in ("BUY", "SELL"):
        await open_position_for_users_bingx(
            symbol=symbol, side=action,
            stop_loss=stop_loss, take_profit_1=take_profit_1,
            take_profit_2=take_profit_2, take_profit_3=take_profit_3,
        )
        await open_position_for_users_okx(
            symbol=symbol, side=action,
            stop_loss=stop_loss, take_profit_1=take_profit_1,
            take_profit_2=take_profit_2, take_profit_3=take_profit_3,
        )
        await notify_users_position_opened(
            symbol=symbol, side=action, entry_price=price,
            stop_loss=stop_loss, take_profit_1=take_profit_1,
            take_profit_2=take_profit_2, take_profit_3=take_profit_3,
        )

    elif action == "MOVE_SL":
        await notify_users_sl_moved_to_breakeven(symbol=symbol)
        await move_sl_to_breakeven_for_all_users(symbol=symbol)
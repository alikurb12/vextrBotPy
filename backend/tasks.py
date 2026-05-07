import asyncio
import logging
import traceback
from celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="process_signal", bind=True, max_retries=3)
def process_signal(self, signal_data):
    try:
        action = signal_data.get('action')
        symbol = signal_data.get('symbol')
        price = signal_data.get('price')
        stop_loss = signal_data.get('stop_loss')
        take_profit_1 = signal_data.get('take_profit_1')
        take_profit_2 = signal_data.get('take_profit_2')
        take_profit_3 = signal_data.get('take_profit_3')
        rsi = signal_data.get('rsi')
        macd = signal_data.get('macd')
        macd_signal = signal_data.get('macd_signal')
        atr = signal_data.get('atr')
        ema_fast = signal_data.get('ema_fast')
        ema_slow = signal_data.get('ema_slow')
        volume = signal_data.get('volume')
        timeframe = signal_data.get('timeframe')

        logger.info(f"⚙️ Обработка сигнала: {action} {symbol}")

        asyncio.run(_process_async(
            action=action, symbol=symbol, price=price,
            stop_loss=stop_loss, take_profit_1=take_profit_1,
            take_profit_2=take_profit_2, take_profit_3=take_profit_3,
            rsi=rsi, macd=macd, macd_signal=macd_signal,
            atr=atr, ema_fast=ema_fast, ema_slow=ema_slow,
            volume=volume, timeframe=timeframe,
        ))

        logger.info(f"✅ Сигнал обработан: {action} {symbol}")
        return {"status": "success"}

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}\n{traceback.format_exc()}")
        raise self.retry(exc=e, countdown=5)


async def _process_async(
    action, symbol, price, stop_loss,
    take_profit_1, take_profit_2, take_profit_3,
    rsi=None, macd=None, macd_signal=None,
    atr=None, ema_fast=None, ema_slow=None,
    volume=None, timeframe=None,
):
    from backend.exchange_apis.bingx.router import open_position_for_users_bingx
    from backend.exchange_apis.okx.router import open_position_for_users_okx
    from backend.utils.send_notification import notify_users_position_opened
    from backend.exchange_apis.bingx.router import move_sl_to_breakeven_for_all_users
    from backend.exchange_apis.okx.router import move_sl_to_breakeven_okx
    from backend.utils.send_notification import notify_users_sl_moved_to_breakeven
    from backend.services.save_successful_trade import save_successful_trades

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
        await save_successful_trades(
            symbol=symbol,
            rsi=rsi, macd=macd, macd_signal=macd_signal,
            atr=atr, ema_fast=ema_fast, ema_slow=ema_slow,
            volume=volume, timeframe=timeframe,
        )
        await notify_users_sl_moved_to_breakeven(symbol=symbol)
        await move_sl_to_breakeven_for_all_users(symbol=symbol)
        await move_sl_to_breakeven_okx(symbol=symbol)

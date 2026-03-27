import asyncio
import logging
import redis
import json
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)
QUEUE_NAME = 'signal_queue'

def process_in_subprocess(signal_data: dict):
    import math
    
    def safe_val(v):
        if v is None:
            return 'None'
        try:
            if math.isnan(float(v)):
                return 'None'
        except (TypeError, ValueError):
            pass
        return repr(v)

    script = f"""
import asyncio
import sys
sys.path.insert(0, '/root/vextr')

async def main():
    from backend.exchange_apis.bingx.router import open_position_for_users_bingx
    from backend.exchange_apis.okx.router import open_position_for_users_okx
    from backend.utils.send_notification import notify_users_position_opened
    from backend.exchange_apis.bingx.router import move_sl_to_breakeven_for_all_users
    from backend.utils.send_notification import notify_users_sl_moved_to_breakeven

    action = {repr(signal_data['action'])}
    symbol = {repr(signal_data['symbol'])}
    price = {safe_val(signal_data['price'])}
    stop_loss = {safe_val(signal_data['stop_loss'])}
    take_profit_1 = {safe_val(signal_data['take_profit_1'])}
    take_profit_2 = {safe_val(signal_data['take_profit_2'])}
    take_profit_3 = {safe_val(signal_data['take_profit_3'])}

    if action in ('BUY', 'SELL'):
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
    elif action == 'MOVE_SL':
        await notify_users_sl_moved_to_breakeven(symbol=symbol)
        await move_sl_to_breakeven_for_all_users(symbol=symbol)

asyncio.run(main())
"""
    result = subprocess.run(
        [sys.executable, '-c', script],
        capture_output=True, text=True,
        env={
            'PYTHONPATH': '/root/vextr',
            'PATH': '/root/vextr/venv/bin:/usr/bin:/bin'
        }
    )
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    return result.returncode == 0

def main():
    logger.info("🚀 Worker запущен, ожидаем сигналы...")
    while True:
        try:
            item = r.blpop(QUEUE_NAME, timeout=5)
            if item is None:
                continue
            _, data = item
            signal = json.loads(data)
            logger.info(f"📥 Получен сигнал: {signal['action']} {signal['symbol']}")
            success = process_in_subprocess(signal)
            if success:
                logger.info(f"✅ Сигнал обработан: {signal['action']} {signal['symbol']}")
            else:
                logger.error(f"❌ Ошибка обработки: {signal['action']} {signal['symbol']}")
        except Exception as e:
            logger.error(f"❌ Ошибка воркера: {e}")

if __name__ == '__main__':
    main()
import asyncio
import logging
import redis
import json
import subprocess
import sys
import warnings
import os

# Подавляем предупреждения на уровне всего приложения
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["PYTHONASYNCIODEBUG"] = "0"

logging.getLogger("aiohttp").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

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

    # Создаем скрипт, который полностью подавляет весь вывод ошибок
    script = f"""
import asyncio
import sys
import warnings
import gc
import os

# Полностью отключаем все предупреждения и вывод
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["PYTHONASYNCIODEBUG"] = "0"

# Отключаем стандартные потоки вывода ошибок
sys.stderr = open(os.devnull, 'w')

# Подавляем вывод aiohttp
import logging
logging.getLogger("aiohttp").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# Импортируем только после подавления вывода
sys.path.insert(0, '/root/vextr')

async def main():
    try:
        from backend.exchange_apis.bingx.router import open_position_for_users_bingx
        from backend.exchange_apis.okx.router import open_position_for_users_okx
        from backend.utils.send_notification import notify_users_position_opened
        from backend.exchange_apis.bingx.router import move_sl_to_breakeven_for_all_users as move_sl_bingx
        from backend.exchange_apis.okx.router import move_sl_to_breakeven_okx as move_sl_okx
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
            await move_sl_bingx(symbol=symbol)
            await move_sl_okx(symbol=symbol)
            
    except Exception as e:
        # Выводим только если это не стандартные сообщения
        msg = str(e)
        if "No active users" not in msg and "нет открытых сделок" not in msg:
            # Используем stdout, так как stderr отключен
            print(f"ERROR: {{msg}}")
    finally:
        # Принудительная очистка
        gc.collect()

# Запускаем с подавлением вывода
try:
    asyncio.run(main())
except Exception:
    pass
finally:
    gc.collect()
"""

    result = subprocess.run(
        [sys.executable, '-c', script],
        capture_output=True, text=True,
        env={
            'PYTHONPATH': '/root/vextr',
            'PATH': '/root/vextr/venv/bin:/usr/bin:/bin',
            'PYTHONWARNINGS': 'ignore',
            'PYTHONASYNCIODEBUG': '0',
        },
        timeout=60
    )
    
    # Выводим только stdout (информационные сообщения)
    if result.stdout:
        # Фильтруем только нужные строки
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Пропускаем все технические сообщения
            if any(skip in line for skip in [
                'Unclosed', 'client_session', 'Fatal error', 'OSError',
                'RuntimeError', 'SSL transport', 'Bad file descriptor',
                'Event loop is closed', 'SSL', 'asyncio', 'Traceback',
                'connections:', 'connector:', 'aiohttp.client_proto',
                'ResponseHandler', 'TCPConnector', 'deque'
            ]):
                continue
            logger.info(line)
    
    # stderr игнорируем полностью
    return result.returncode == 0

def main():
    logger.info("🚀 Worker запущен, ожидаем сигналы...")
    error_count = 0
    
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
                error_count = 0
            else:
                error_count += 1
                if error_count <= 3:  # Выводим ошибку только если их немного
                    logger.error(f"❌ Ошибка обработки: {signal['action']} {signal['symbol']}")
                
                if error_count > 5:
                    logger.warning("⚠️ Слишком много ошибок, пауза 10 секунд...")
                    import time
                    time.sleep(10)
                    error_count = 0
                    
        except Exception as e:
            error_count += 1
            if error_count <= 3:
                logger.error(f"❌ Ошибка воркера: {e}")
            if error_count > 5:
                import time
                time.sleep(10)
                error_count = 0

if __name__ == '__main__':
    main()
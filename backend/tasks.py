# backend/tasks.py
import asyncio
import logging
import traceback
from celery import Task
from celery.exceptions import Retry
from celery_app import celery_app

logger = logging.getLogger(__name__)

class SignalTask(Task):
    """Базовый класс для задач с asyncio"""
    _loop = None
    
    def __call__(self, *args, **kwargs):
        # Создаем новый event loop для каждой задачи
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            return super().__call__(*args, **kwargs)
        finally:
            # Закрываем loop после выполнения
            try:
                # Отменяем все ожидающие задачи
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            except Exception:
                pass
            finally:
                self._loop.close()

@celery_app.task(base=SignalTask, bind=True, max_retries=3, default_retry_delay=60)
def process_signal(self, signal_data):
    """Обработка торгового сигнала"""
    try:
        action = signal_data.get('action')
        symbol = signal_data.get('symbol')
        
        logger.info(f"📥 Обработка сигнала: {action} {symbol}")
        
        # Получаем текущий loop (создан в SignalTask.__call__)
        loop = asyncio.get_event_loop()
        
        if action in ('BUY', 'SELL'):
            from backend.exchange_apis.bingx.router import open_position_for_users_bingx
            from backend.exchange_apis.okx.router import open_position_for_users_okx
            from backend.utils.send_notification import notify_users_position_opened
            
            price = signal_data.get('price')
            stop_loss = signal_data.get('stop_loss')
            take_profit_1 = signal_data.get('take_profit_1')
            take_profit_2 = signal_data.get('take_profit_2')
            take_profit_3 = signal_data.get('take_profit_3')
            
            # Выполняем асинхронные операции в текущем loop
            loop.run_until_complete(open_position_for_users_bingx(
                symbol=symbol, side=action,
                stop_loss=stop_loss, take_profit_1=take_profit_1,
                take_profit_2=take_profit_2, take_profit_3=take_profit_3,
            ))
            
            loop.run_until_complete(open_position_for_users_okx(
                symbol=symbol, side=action,
                stop_loss=stop_loss, take_profit_1=take_profit_1,
                take_profit_2=take_profit_2, take_profit_3=take_profit_3,
            ))
            
            loop.run_until_complete(notify_users_position_opened(
                symbol=symbol, side=action, entry_price=price,
                stop_loss=stop_loss, take_profit_1=take_profit_1,
                take_profit_2=take_profit_2, take_profit_3=take_profit_3,
            ))
            
        elif action == 'MOVE_SL':
            from backend.exchange_apis.bingx.router import move_sl_to_breakeven_for_all_users as move_sl_bingx
            from backend.exchange_apis.okx.router import move_sl_to_breakeven_okx as move_sl_okx
            from backend.utils.send_notification import notify_users_sl_moved_to_breakeven
            
            loop.run_until_complete(notify_users_sl_moved_to_breakeven(symbol=symbol))
            loop.run_until_complete(move_sl_bingx(symbol=symbol))
            loop.run_until_complete(move_sl_okx(symbol=symbol))
            
        else:
            logger.error(f"Неизвестное действие: {action}")
            return {"status": "error", "message": f"Unknown action: {action}"}
        
        logger.info(f"✅ Сигнал {action} {symbol} обработан успешно")
        return {"status": "success", "signal": signal_data}
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке сигнала: {e}")
        logger.error(traceback.format_exc())
        
        # Автоматический повтор при ошибке
        try:
            self.retry(exc=e, countdown=60)
        except Retry:
            raise
        except Exception as retry_exc:
            logger.error(f"Не удалось повторить задачу: {retry_exc}")
            return {"status": "error", "message": str(e)}

@celery_app.task
def send_test_signal():
    """Тестовая задача"""
    test_signal = {
        "action": "MOVE_SL",
        "symbol": "TESTUSDT.P"
    }
    process_signal.delay(test_signal)
    return {"status": "sent", "signal": test_signal}
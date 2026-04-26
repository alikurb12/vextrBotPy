import datetime
import logging
from database.models.trades.dao import TradesDAO
from database.models.users.dao import UsersDAO
from backend.exchange_apis.okx.services.get_open_positions import get_open_positions as get_open_positions_okx

log = logging.getLogger(__name__)

async def sync_trades_for_user(user):
    """
    Синхронизирует сделки в БД с реальными позициями на бирже.
    Если сделка в БД помечена как 'open', но на бирже её нет — закрываем её в БД.
    """
    try:
        trades_in_db = await TradesDAO.get_all(user_id=user.user_id, status="open")
        if not trades_in_db:
            log.info(f"Нет открытых сделок в БД для пользователя id={user.user_id}")
            return

        if user.exchange == "OKX":
            positions_on_exchange = await get_open_positions_okx(
                api_key=user.api_key,
                secret_key=user.secret_key,
                passphrase=user.passphrase,
            )
        else:
            log.info(f"Биржа {user.exchange} пока не поддерживается для синхронизации")
            return

        # Символы которые реально открыты на бирже
        open_symbols = set()
        if positions_on_exchange:
            for pos in positions_on_exchange:
                size = float(pos.get("pos", 0) or 0)
                if size != 0:
                    # OKX возвращает символ в формате BTC-USDT-SWAP
                    # конвертируем в формат БД
                    inst_id = pos.get("instId", "")
                    symbol = inst_id.replace("-SWAP", "").replace("-", "-")
                    open_symbols.add(symbol)
                    open_symbols.add(inst_id)  # добавляем оба варианта

        log.info(f"Открытые позиции на OKX для id={user.user_id}: {open_symbols}")

        # Проверяем каждую сделку в БД
        for trade in trades_in_db:
            symbol_normalized = trade.symbol.replace("-SWAP", "")
            if trade.symbol not in open_symbols and symbol_normalized not in open_symbols:
                log.info(
                    f"Сделка id={trade.trade_id} symbol={trade.symbol} "
                    f"пользователя id={user.user_id} не найдена на бирже — закрываем в БД"
                )
                await TradesDAO.update(
                    trade_id=trade.trade_id,
                    status="closed",
                    closed_at=datetime.datetime.now(),
                )

    except Exception as e:
        log.error(f"Ошибка синхронизации сделок пользователя id={user.user_id}: {e}")


async def sync_all_users_trades():
    """Синхронизирует сделки для всех пользователей."""
    try:
        users_okx = await UsersDAO.get_all(exchange="okx")
        all_users = (users_okx or [])
        
        if not all_users:
            log.info("Нет пользователей для синхронизации")
            return

        for user in all_users:
            if user.api_key and user.secret_key:
                await sync_trades_for_user(user)

        log.info("Синхронизация сделок завершена")
    except Exception as e:
        log.error(f"Ошибка при синхронизации всех сделок: {e}")

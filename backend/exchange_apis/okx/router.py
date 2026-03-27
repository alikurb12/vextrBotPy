from database.models.users.dao import UsersDAO
from database.models.trades.dao import TradesDAO
from backend.exchange_apis.okx.services.close_position import close_position
from backend.exchange_apis.okx.services.get_balance import get_balance
from backend.exchange_apis.okx.services.set_leverage import set_leverage
from backend.exchange_apis.okx.services.open_position import open_position
from backend.exchange_apis.okx.services.get_symbol_info import get_symbol_info
from backend.exchange_apis.okx.services.set_sl_order import set_sl_order
from backend.exchange_apis.okx.services.set_tp_order import set_tp_orders
from backend.exchange_apis.okx.services.move_sl_to_breakeven import move_sl_to_breakeven
import datetime
import math
import logging

log = logging.getLogger(__name__)

async def open_position_for_users_okx(
        symbol : str,
        side : str,
        stop_loss : float,
        take_profit_1 : float,
        take_profit_2 : float,
        take_profit_3 : float,
):
    symbol = symbol.replace(".P", "").replace("USDT", "-USDT") + "-SWAP"
    side = "long" if side == "BUY" else "short"
    users = await UsersDAO.get_all(exchange="OKX")
    if not users:
        print("Нет активных пользователей с подпиской okx")
        return
    
    for i, user in enumerate(users, 1):
        if not user.api_key or not user.secret_key:
            print(f"У пользователя id = {user.user_id}'; username = '{user.usename}' нет АПИ и/или Секрет ключей")
            continue
        try:
            existing_trades = await TradesDAO.get_all(user_id=user.user_id, symbol=symbol, status="open")
            if existing_trades:
                for trade in existing_trades:
                    print(f"У пользователя id='{user.user_id}' уже есть открытая сделка по {symbol}. Переворачиваем сделку")
                    try:
                        await close_position(
                            api_key=user.api_key,
                            secret_key=user.secret_key,
                            passphrase=user.passphrase,
                            symbol=symbol,
                            position_syde="short" if side == "long" else "long",
                        )
                        print(f"Сделка id='{trade.trade_id}' пользователя id='{user.user_id}' успешно закрыта.")
                        await TradesDAO.delete(trade_id=trade.trade_id)
                    except Exception as e:
                        print(f"Ошибка при закрытии сделки пользователя id='{user.user_id}': {e}")
                        continue
            user_balance = await get_balance(
                api_key=user.api_key, 
                secret_key=user.secret_key,
                passphrase=user.passphrase,
            )
            await set_leverage(
                api_key=user.api_key,
                secret_key=user.secret_key,
                passphrase=user.passphrase,
                symbol=symbol,
                position_side=side,
            )

            print("Выставлено 5х плечо для сделки")
            symbol_info = await get_symbol_info(symbol=symbol)
            raw_quantity = (float(user_balance) * 0.05 * 10) / (symbol_info["last_price"] * symbol_info["ct_val"])
            lot_sz = symbol_info["lot_sz"]
            quantity = math.floor(raw_quantity / lot_sz) * lot_sz
            quantity = round(quantity, 8)

            print(f"Расчёт quantity: баланс={user_balance}, цена={symbol_info['last_price']}, ctVal={symbol_info['ct_val']}, lotSz={lot_sz} -> quantity={quantity}")

            order = await open_position(
                api_key=user.api_key,
                secret_key=user.secret_key,
                passphrase=user.passphrase,
                symbol=symbol,
                position_side=side,
                quantity=str(quantity),
            )
            log.info(f"order response: {order}")
            if not order or order.get("code") != "0":
                log.error(f"Ошибка открытия позиции для пользователя id='{user.user_id}': {order}")
                continue
            log.info(f"Открыта сделка '{symbol}' для пользователя id='{user.user_id}'.")

            sl_order = await set_sl_order(
                api_key=user.api_key,
                secret_key=user.secret_key,
                passphrase=user.passphrase,
                symbol=symbol,
                position_side=side,
                sl_price=stop_loss,
                quantity=str(quantity),
            )
            print(f"Выставление стоп-лосса для пользователя id={user.user_id}")
            print(f"sl_order response: {sl_order}")
            tp_orders = await set_tp_orders(
                api_key=user.api_key,
                secret_key=user.secret_key,
                passphrase=user.passphrase,
                symbol=symbol,
                position_side=side,
                quantity=quantity,
                tp_prices=[take_profit_1, take_profit_2, take_profit_3],
            )
            print(f"Выставление тейк-профитов для пользователя id={user.user_id}")

            order_id = order["data"][0]["ordId"]
            sl_order_id = sl_order["data"][0]["algoId"]

            tp1_order_id = tp_orders[0]["data"][0]["algoId"] if len(tp_orders) > 0 else None
            tp2_order_id = tp_orders[1]["data"][0]["algoId"] if len(tp_orders) > 1 else None
            tp3_order_id = tp_orders[2]["data"][0]["algoId"] if len(tp_orders) > 2 else None

            order_id = order["data"][0]["ordId"]

            # Безопасное получение ID ордеров
            sl_order_id = sl_order["data"][0]["algoId"] if sl_order and sl_order.get("code") == "0" else None
            tp1_order_id = tp_orders[0]["data"][0]["algoId"] if len(tp_orders) > 0 and tp_orders[0].get("code") == "0" else None
            tp2_order_id = tp_orders[1]["data"][0]["algoId"] if len(tp_orders) > 1 and tp_orders[1].get("code") == "0" else None
            tp3_order_id = tp_orders[2]["data"][0]["algoId"] if len(tp_orders) > 2 and tp_orders[2].get("code") == "0" else None

            try:
                await TradesDAO.add(
                    user_id=user.user_id,
                    order_id=order_id,
                    symbol=symbol,
                    side=side,
                    position_side=side,
                    quantity=quantity,
                    entry_price=symbol_info["last_price"],
                    status="open",
                    created_at=datetime.datetime.now(),
                    exchange=user.exchange,
                    stop_loss=stop_loss,
                    sl_order_id=sl_order_id,
                    take_profit_1=take_profit_1,
                    take_profit_2=take_profit_2,
                    take_profit_3=take_profit_3,
                    tp1_order_id=tp1_order_id,
                    tp2_order_id=tp2_order_id,
                    tp3_order_id=tp3_order_id,
                )
                print("Запись по открытой сделке добавлена в БД")
            except Exception as db_error:
                print(f"Ошибка сохранения в БД для OKX: {db_error}")

        except Exception as e:
            print(f"Исключение при открытии сделки: {e}")

async def move_sl_to_breakeven_okx(
        symbol : str
):
    symbol = symbol.replace(".P", "").replace("USDT", "-USDT") + "-SWAP" 
    users = await UsersDAO.get_all(exchange="OKX")
    if not users:
        print("Нет активных пользователей с подпиской okx")
    
    for i, user in enumerate(users, 1):
        if not user.api_key or not user.secret_key:
            print(f"У пользователя id = {user.user_id}'; username = '{user.usename}' нет АПИ и/или Секрет ключей")
            continue
        try:
            trades = await TradesDAO.get_all(user_id=user.user_id, symbol=symbol, status="open")
            if not trades:
                print(f"У пользователя id='{user.user_id}' нет открытых сделок по '{symbol}'")
                continue
            
            for trade in trades:
                await move_sl_to_breakeven(
                    api_key = user.api_key,
                    secret_key = user.secret_key,
                    symbol = trade.symbol,
                    position_side = trade.side,
                    quantity = trade.quantity,
                    entry_price = trade.entry_price,
                    sl_order_id = trade.sl_order_id
                )
                print(f"SL успешно перемещён в безубыток для сделки id='{trade.trade_id}' пользователя id='{user.user_id}'")
                await TradesDAO.update(
                    trade_id = trade.trade_id,
                    stop_loss = trade.entry_price,
                    sl_order_id = None,
                    status = "sl_moved_to_breakeven",
                )
        except Exception as e:
            print(f"Ошибка при перемещении SL в безубыток для пользователя id='{user.user_id}': {e}")

from database.models.users.dao import UsersDAO
from database.models.trades.dao import TradesDAO
from backend.exchange_apis.bingx.services.get_balance import get_balance
from backend.exchange_apis.bingx.services.create_main_order import create_main_order
from backend.exchange_apis.bingx.services.set_leverage import set_leverage
from backend.exchange_apis.bingx.services.set_sl_order import set_sl_order
from backend.exchange_apis.bingx.services.set_tp_orders import set_tp_orders
from backend.exchange_apis.bingx.services.move_sl_to_breakeven import move_sl_to_breakeven
from backend.exchange_apis.bingx.services.close_position import close_position
import datetime

async def get_users_balances():
    users = await UsersDAO.get_all()
    if not users:
        print("Нет активных пользователей")
        return
    for i, user in enumerate(users, 1):
        if not user.api_key or not user.secret_key:
            print(f"У пользователя id = {user.user_id}'; username = '{user.usename}' нет АПИ и/или Секрет ключей")
            continue
        try:
            user_balance = await get_balance(user.api_key, user.secret_key)
            print(f"Пользователь '{user.username}' id='{user.user_id}' Баланс={user_balance.get('data').get('data').get('balance').get('balance')}")
        except Exception as e:
            print(f"Ошибка: {e}")

async def open_position_for_all_users(
        symbol : str,
        side : str,
        stop_loss : float,
        take_profit_1 : float,
        take_profit_2 : float,
        take_profit_3 : float,
):
    users = await UsersDAO.get_all()
    if not users:
        print("Нет активных пользователей")
    
    for i, user in enumerate(users, 1):
        if not user.api_key or not user.secret_key:
            print(f"У пользователя id = {user.user_id}'; username = '{user.usename}' нет АПИ и/или Секрет ключей")
            continue
        try:
            existing_trades = await TradesDAO.get_all(user_id=user.user_id, symbol=symbol, status="open")
            if existing_trades:
                for trade in existing_trades:
                    print(f"У пользователя id='{user.user_id}' уже есть открытая сделка по '{symbol}'. Переворачиваем сделку")
                    try:
                        await close_position(
                            api_key=user.api_key,
                            secret_key=user.secret_key,
                            symbol=symbol,
                        )
                        print(f"Сделка id='{trade.trade_id}' пользователя id='{user.user_id}' успешно закрыта.")
                        await TradesDAO.delete(trade_id=trade.trade_id)
                    except Exception as e:
                        print(f"Ошибка при закрытии сделки пользователя id='{user.user_id}': {e}")
                        continue
            user_balance = await get_balance(user.api_key, user.secret_key)
            user_balance = float(user_balance.get('data').get('data').get('balance').get('balance'))
            
            await set_leverage(
                symbol=symbol,
                api_key = user.api_key,
                side=side,
                secret_key = user.secret_key,
            )
            print("Выставлено 5х плечо для сделки")
            
            order = await create_main_order(
                symbol=symbol,
                api_key = user.api_key,
                secret_key = user.secret_key,
                side=side,
                quantity=user_balance*0.05 * 10, 
            )
            print(f"Открыта сделка '{symbol}' для пользователя id='{user.user_id}'.")
            

            sl_order = await set_sl_order(
                api_key = user.api_key,
                secret_key = user.secret_key,
                symbol = symbol,
                price = stop_loss,
                side = side,
                quantity=float(order.get("order").get("executedQty")),
            )
            
            print(f"Выставление стоп-лосса для пользователя id={user.user_id}")

            tp_orders = await set_tp_orders(
                api_key = user.api_key,
                secret_key = user.secret_key,
                symbol = symbol,
                side = side,
                quantity = float(order.get("order").get("quantity")),
                tp_prices = [take_profit_1, take_profit_2, take_profit_3],
            )
            print(f"Выставление тейк-профитов для пользователя id={user.user_id}")

            await TradesDAO.add(
                user_id = user.user_id,
                order_id = str(order.get("order").get("orderId")),
                symbol = order.get("order").get("symbol"),
                side = side,
                position_side = order.get("order").get("positionSide"),
                quantity = float(order.get("order").get("quantity")),
                entry_price = float(order.get("order").get("avgPrice")),
                status = "open",
                created_at = datetime.datetime.now(),
                exchange = user.exchange,
                stop_loss = stop_loss,
                sl_order_id = str(sl_order.get("order").get("orderId")),
                take_profit_1 = take_profit_1,
                take_profit_2 = take_profit_2,
                take_profit_3 = take_profit_3,
                tp1_order_id = str(tp_orders[0].get("order").get("orderId"))
                if len(tp_orders) > 0 else None,
                tp2_order_id = str(tp_orders[1].get("order").get("orderId"))
                if len(tp_orders) > 1 else None,
                tp3_order_id = str(tp_orders[2].get("order").get("orderId"))
                if len(tp_orders) > 2 else None,
            )
            print("Запись по открытой сделке добавлено в БД")
        except Exception as e:
            print(f"Ошибка при открытии сделки: {e}")


async def move_sl_to_breakeven_for_all_users(
        symbol : str,
):
    users = await UsersDAO.get_all()
    if not users:
        print("Нет активных пользователей")
    
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
                    side = trade.side,
                    quantity = trade.quantity,
                    entry_price = trade.entry_price,
                    sl_order_id = int(trade.sl_order_id),
                )
                print(f"SL успешно перемещён в безубыток для сделки id='{trade.trade_id}' пользователя id='{user.user_id}'")
                TradesDAO.update(
                    trade_id = trade.trade_id,
                    stop_loss = trade.entry_price,
                    sl_order_id = None,
                    status = "sl_moved_to_breakeven",
                )
        except Exception as e:
            print(f"Ошибка при перемещении SL в безубыток для пользователя id='{user.user_id}': {e}")

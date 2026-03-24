import okx.Trade as Trade
from config.config import settings
from backend.exchange_apis.okx.services.close_order import close_order
from backend.exchange_apis.okx.services.set_sl_order import set_sl_order

async def move_sl_to_breakeven(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_side : str,
        quantity : str,
        entry_price : str,
        sl_order_id : str,

):
    try:
        await close_order(
            api_key=api_key,
            secret_key=secret_key,
            passphrase=passphrase,
            symbol=symbol,
            order_id=sl_order_id,
        )
        print(f"SL ордер {sl_order_id} успешно отменён")

        result = await set_sl_order(
            api_key=api_key,
            secret_key=secret_key,
            passphrase=passphrase,
            symbol=symbol,
            position_side=position_side,
            sl_price=entry_price,
            quantity=quantity,
        )
        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при перемещении SL на безубыток: {result.get('data')[0].get('sMsg')}")
            return None
    except Exception as e:
        print(f"Исключение при перемещении SL на безубыток: {e}")
        return None


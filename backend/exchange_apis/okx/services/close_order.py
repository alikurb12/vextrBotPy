import okx.Trade as Trade
from config.config import settings

async def close_order(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        order_id : str,
):
    try:
        trade = Trade.TradeAPI(
            api_key=api_key,
            api_secret_key=secret_key,
            passphrase=passphrase,
            flag=settings
        )

        result = trade.cancel_order(
            instId=symbol,
            ordId=order_id,
        )

        if result["code"] == 0:
            return result
        else:
            print(f"Ошибка при закрытии ордера: {result}")
            return None
    except Exception as e:
        print(f"Исключение при закрытии ордера: {e}")
        return None
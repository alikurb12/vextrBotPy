import okx.Trade as Trade
from config.config import settings
async def open_position(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_side : str,
        quantity : str,
):
    try:
        trade = Trade.TradeAPI(
            api_key=api_key,
            api_secret_key=secret_key,
            passphrase=passphrase,
            flag=settings.OKX_FLAG,
        )

        result = trade.place_order(
            instId=symbol,
            tdMode="isolated",
            side="buy" if position_side.lower() == "long" else "sell",
            posSide=position_side.lower(),
            ordType="market",
            sz=quantity,
        )

        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при открытии позиции: {result}")
            return None
    except Exception as e:
        print(f"Исключение при открытии позиции: {e}")
        return None
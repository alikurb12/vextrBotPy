import okx.Trade as Trade
from config.config import settings

async def set_tp_order(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_side : str,
        tp_price : float,
        quantity : str,
):
    try:
        trade = Trade.TradeAPI(
            api_key=api_key,
            api_secret_key=secret_key,
            passphrase=passphrase,
            flag=settings.OKX_FLAG,
        )
        result = trade.place_algo_order(
            instId=symbol,
            tdMode="isolated",
            side="buy" if position_side.lower() == "short" else "sell",
            posSide=position_side.lower(),
            ordType="conditional",
            sz=quantity,
            tpTriggerPx=str(tp_price),
            tpOrdPx="-1",
        )

        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при выставлении тейк-профита: {result}")
            return None
    except Exception as e:
        print(f"Исключение при выставлении тейк-профита: {e}")
        return None
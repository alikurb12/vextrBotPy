import okx.Trade as Trade
from config.config import settings

async def set_sl_order(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_side : str,
        sl_price : float,
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
            slTriggerPx=str(sl_price),
            slOrdPx="-1",
        )

        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при выставлении стоп лосса: {result.get('data')[0].get('sMsg')}")
            return None
    except Exception as e:
        print(f"Искулючение при выставлении стоп лосса: {e}")
        return None
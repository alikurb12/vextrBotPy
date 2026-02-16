import httpx
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign
import time

async def set_sl_order(
        api_key : str,
        secret_key : str,
        symbol : str,
        price : float,
        side : str,
        quantity: float,
): 
    try:
        path = "/openApi/swap/v2/trade/order"
        paramsMap = {
            "type": "STOP_MARKET",
            "symbol" : symbol,
            "side" : side,
            "positionSide" : "LONG" if side=="SELL" else "SHORT",
            "quantity" : quantity,
            "stopPrice" : price,
            "timestamp" : int(time.time() * 1000),
        }
        paramsStr = await parseParam(paramsMap=paramsMap)
        signature = get_sign(secret_key=secret_key, payload=paramsStr)
        url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

        headers = {
            'X-BX-APIKEY': api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
            data = response.json()
            if data.get("code") != 0:
                error_msg = data.get("msg", "Unknown error")
                print(f"Детали ошибки: {data}")
                raise ValueError(f"Ошибка при выставлении стоп-лосса: {error_msg}")
            return data.get("data")

    except Exception as e:
        print(f"Ошибка при выставлении стоп-лосса: {e}")
        raise
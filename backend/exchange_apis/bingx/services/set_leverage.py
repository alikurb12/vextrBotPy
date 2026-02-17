import httpx
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign
import time

async def set_leverage(
        symbol : str,
        api_key : str,
        side : str,
        secret_key : str,
):
    leverage = settings.LEVERAGE_LEVEL

    try:
        path = "/openApi/swap/v2/trade/leverage"
        paramsMap = {
            "symbol" : symbol,
            "side" : "LONG" if side=="BUY" else "SHORT",
            "timestamp" : int(time.time() * 1000),
            "leverage" : leverage
        }
        paramsStr = await parseParam(paramsMap)
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
                raise ValueError(f"Ошибка при установке торгового плеча: {error_msg}")
            return data.get("data")
    
    except Exception as e:
        print(f"Ошибка при установке торгового плеча: {e}")
        raise
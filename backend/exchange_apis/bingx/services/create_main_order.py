import httpx
import time
import uuid
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign

async def create_main_order(
        symbol: str,
        api_key: str,
        secret_key: str,
        side: str,
        quantity: float,
):
    try:
        path = "/openApi/swap/v2/trade/order"
        
        client_order_id = f"order_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        paramsMap = {
            "symbol": symbol,
            "side": side,
            "positionSide": "LONG" if side == "BUY" else "SHORT",
            "type": "MARKET",
            "quantity": str(quantity),
            "timestamp": int(time.time() * 1000),
            "clientOrderID": client_order_id
        }
        paramsStr = await parseParam(paramsMap=paramsMap)
        
        signature = get_sign(secret_key=secret_key, payload=paramsStr)
        url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

        headers = {
            'X-BX-APIKEY': api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url=url, headers=headers)
            data = response.json()
            if data.get("code") != 0:
                error_msg = data.get("msg", "Unknown error")
                print(f"Детали ошибки: {data}")
                raise ValueError(f"Ошибка при открытии сделки: {error_msg}")
            return data.get("data")
    
    except Exception as e:
        print(f"Ошибка при открытии сделки: {e}")
        raise
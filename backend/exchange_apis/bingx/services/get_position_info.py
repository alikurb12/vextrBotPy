import httpx
import time
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign

async def get_position_info(
    api_key: str,
    secret_key: str,
    symbol: str
):
    """
    Получение информации о позиции по символу
    """
    try:
        path = "/openApi/swap/v2/user/positions"
        paramsMap = {
            "symbol": symbol,
            "timestamp": int(time.time() * 1000)
        }
        
        paramsStr = await parseParam(paramsMap)
        signature = get_sign(secret_key=secret_key, payload=paramsStr)
        url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"
        
        headers = {
            "X-BX-APIKEY": api_key,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            data = response.json()
            
            if data.get("code") != 0:
                if data.get("code") == 109420:  # position not exist
                    return None
                raise ValueError(f"Ошибка получения позиции: {data.get('msg')}")
            
            positions = data.get("data", [])
            # Ищем нужную позицию
            for pos in positions:
                if pos.get("symbol") == symbol:
                    return pos
            return None
            
    except Exception as e:
        print(f"Ошибка в get_position_info: {e}")
        raise
import httpx
import time
from config.config import settings
from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign

async def close_position(
        symbol : str,
        api_key : str,
        secret_key : str,
):
    try:
        path = "/openApi/swap/v1/trade/closePosition"

        positions = await get_open_positions(api_key=api_key, secret_key=secret_key)
        if not positions:
            print("Сейчас нет открытых позиций")
            return None
        
        target_position = None
        for position in positions:
            pos_symbol = position.get("symbol")
            if pos_symbol == symbol:
                target_position = position
                print(target_position)
                break
        if not target_position:
            print("Нет такой открытой позиции")
            return None
        
        position_id = target_position.get("positionId")
        if not position_id:
            print("Не удалось получить id позиции")
            return None
        
        paramsMap = {
            "positionId" : position_id,
            "timestamp" : int(time.time() * 1000)
        }
        paramsStr = await parseParam(paramsMap=paramsMap)

        signature = get_sign(secret_key=secret_key, payload=paramsStr)
        url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

        headers = {
            'X-BX-APIKEY': api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with httpx.AsyncClient() as client:
            responce = await client.post(url=url, headers=headers)
            data = responce.json()
            if data.get("code") != 0:
                error_msg = data.get("msg")
                print(f"Ошибка при закртытии сделки: {error_msg}")
                raise ValueError("Ошибка при открытии сделки")
            return data.get("data")
    except Exception as e:
        print(f"Ошибка при открыии сделки: {e}")
        raise
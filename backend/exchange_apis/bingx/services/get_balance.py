import httpx
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign
from typing import Dict
from config.config import settings

async def get_balance(api_key: str, secret_key: str) -> Dict:
    try:
        path = '/openApi/swap/v2/user/balance'
        paramsMap = {}
        paramsStr = await parseParam(paramsMap)

        signature = get_sign(secret_key, paramsStr)
        url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

        headers = {
            'X-BX-APIKEY': api_key,
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            responce = await client.get(url=url, headers=headers)
            data = responce.json()
            if data.get("code") != 0:
                error_msg = data.get("msg")
                raise ValueError(f"Ошибка при получении баланса {error_msg}")
            
            return {
                "result" : "success",
                "data" : data
                }
    except httpx.RequestError as e:
        raise ValueError(f"Сетевая ошибка при получении баланса {e}")
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")
        raise
import httpx
from config.config import settings
from backend.exchange_apis.bingx.services.get_sign import get_sign
from backend.exchange_apis.bingx.services.parseParam import parseParam

async def get_open_positions(
        api_key: str,
        secret_key: str,
):
    try:
        path = "/openApi/swap/v2/user/positions"
        paramsMap = {}
        paramsStr = await parseParam(paramsMap=paramsMap)

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
                raise ValueError(f"Ошибка при получении открытых позиций: {error_msg}")
            return data.get("data")
    
    except Exception as e:
        print(f"Ошибка при получении открытых позиций: {e}")
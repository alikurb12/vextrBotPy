import httpx
from config.config import settings


async def get_current_price(symbol: str) -> float:
    try:
        url = f"{settings.BINGX_API_URL}/openApi/swap/v2/quote/price?symbol={symbol}"
        
        async with httpx.AsyncClient() as client:
            responce = await client.get(url=url)
            data = responce.json()
            if data.get("code") != 0:
                error_msg = data.get("msg")
                raise ValueError(f"Ошибка при получении текущей цены {error_msg}")
            return float(data.get("data", {}).get("price", 0))
    except httpx.RequestError as e:
        raise ValueError(f"Сетевая ошибка при получении текущей цены {e}")
    except Exception as e:
        print(f"Ошибка при получении текущей цены: {e}")
        raise
import httpx
from config.config import settings

async def get_symbol_info(symbol: str) -> dict:
    try:
        url = f"{settings.BINGX_API_URL}/openApi/swap/v2/quote/contracts"
        
        async with httpx.AsyncClient() as client:
            responce = await client.get(url=url)
            data = responce.json()
            if 'data' in data:
                for contract in data['data']:
                    if contract['symbol'] == symbol:
                        return {
                            "minQty": contract.get("tradeMinQuantity"),
                            "stepSize": contract.get("quantityPrecision"),
                            "minUSDT" : contract.get("tradeMinUSDT")
                        }
        raise ValueError(f"Пара {symbol} не найдена")
    except httpx.RequestError as e:
        raise ValueError(f"Сетевая ошибка при получении информации о символе {e}")
    except Exception as e:
        print(f"Ошибка при получении информации о символе: {e}")
        raise
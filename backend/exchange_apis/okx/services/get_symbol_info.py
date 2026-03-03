import okx.MarketData as Market
from config.config import settings

async def get_symbol_info(
        symbol : str
):
    try:
        market = Market.MarketAPI(flag=settings.OKX_FLAG)
        result = market.get_ticker(instId=symbol)

        if result["code"] == "0":
            return result #result['data'][0].get('last')
        else:
            print(f"Ошибка при получении информации по монете: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при получении информации по монете: {e}")
        return None
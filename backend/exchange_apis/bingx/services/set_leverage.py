import httpx
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam

async def set_leverage(
        symbol : str,
        leverage : int,
        position_slide : str,
        api_key : str,
        secret_key : str,
):
    leverage = settings.LEVERAGE_LEVEL

    try:
        url = f"{settings.BINGX_API_URL}/openApi/swap/v2/trade/leverage"
        paramsMap = {
            "symbol" : symbol,
            "leverage" : leverage,
            "position_slide" : position_slide,
        }
        paramsStr = await parseParam(paramsMap)
        async with httpx.AsyncClient() as client:
            pass
    except Exception as e:
        raise ValueError(f"Ошибка при установлении торгового плеча: {e}")
import okx.MarketData as Market
import okx.PublicData as PublicData
from config.config import settings


async def get_symbol_info(symbol: str) -> dict | None:
    try:
        market = Market.MarketAPI(flag=settings.OKX_FLAG)
        ticker_result = market.get_ticker(instId=symbol)

        if ticker_result["code"] != "0":
            print(f"Ошибка при получении тикера: {ticker_result['msg']}")
            return None

        last_price = float(ticker_result["data"][0].get("last"))

        public = PublicData.PublicAPI(flag=settings.OKX_FLAG)
        inst_result = public.get_instruments(instType="SWAP", instId=symbol)

        if inst_result["code"] != "0" or not inst_result.get("data"):
            print(f"Ошибка при получении инструмента: {inst_result['msg']}")
            return None

        inst = inst_result["data"][0]
        ct_val = float(inst.get("ctVal"))
        lot_sz = float(inst.get("lotSz"))

        return {
            "last_price": last_price,
            "ct_val": ct_val,
            "lot_sz": lot_sz,
        }

    except Exception as e:
        print(f"Исключение при получении информации по монете: {e}")
        return None
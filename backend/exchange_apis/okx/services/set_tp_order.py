import math
import okx.Trade as Trade
import okx.PublicData as PublicData
from config.config import settings

INSUFFICIENT_MARGIN_CODES = {"51008", "51010", "51131", "51132"}


def _is_margin_error(exc: Exception) -> bool:
    msg = str(exc)
    for part in msg.split("|"):
        if part.startswith("code="):
            code = part.split("=", 1)[1]
            if code in INSUFFICIENT_MARGIN_CODES:
                return True
    margin_keywords = ("insufficient margin", "margin", "insufficient")
    return any(kw in msg.lower() for kw in margin_keywords)


def _get_lot_size(symbol: str) -> float:
    public = PublicData.PublicAPI(flag=settings.OKX_FLAG)
    result = public.get_instruments(instType="SWAP", instId=symbol)
    if result.get("code") != "0" or not result.get("data"):
        raise ValueError(f"Не удалось получить данные инструмента {symbol}: {result}")
    lot_sz = float(result["data"][0]["lotSz"])
    return lot_sz


def _split_quantity(quantity: float, n: int, lot_sz: float) -> list[float]:
    total_lots = math.floor(quantity / lot_sz)
    lots_per_part = total_lots // n
    remainder_lots = total_lots - lots_per_part * n

    parts = [round(lots_per_part * lot_sz, 8)] * n
    parts[0] = round((lots_per_part + remainder_lots) * lot_sz, 8)

    parts = [p for p in parts if p > 0]
    return parts


def _place_single_tp_order(
    trade: Trade.TradeAPI,
    symbol: str,
    position_side: str,
    quantity: float,
    price: float,
):
    result = trade.place_algo_order(
        instId=symbol,
        tdMode="isolated",
        side="buy" if position_side.lower() == "short" else "sell",
        posSide=position_side.lower(),
        ordType="conditional",
        sz=str(quantity),
        tpTriggerPx=str(price),
        tpOrdPx="-1",
    )

    if result.get("code") != "0":
        error_code = result.get("code", "unknown")
        error_msg = result.get("msg", "Unknown error")
        print(f"Детали ошибки TP на цене {price}: {result}")
        raise ValueError(f"code={error_code}|msg={error_msg}|price={price}")

    return result


async def set_tp_orders(
    api_key: str,
    secret_key: str,
    passphrase: str,
    symbol: str,
    position_side: str,
    quantity: float,
    tp_prices: list[float],
):
    if not tp_prices:
        raise ValueError("tp_prices не может быть пустым")

    tp_prices = tp_prices[:3]

    lot_sz = _get_lot_size(symbol)
    quantities = _split_quantity(quantity, len(tp_prices), lot_sz)

    tp_prices = tp_prices[:len(quantities)]

    trade = Trade.TradeAPI(
        api_key=api_key,
        api_secret_key=secret_key,
        passphrase=passphrase,
        flag=settings.OKX_FLAG,
    )

    try:
        results = []
        errors = []

        for price, qty in zip(tp_prices, quantities):
            try:
                result = _place_single_tp_order(
                    trade=trade,
                    symbol=symbol,
                    position_side=position_side,
                    quantity=qty,
                    price=price,
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        if not errors:
            print(f"Успешно выставлены {len(results)} TP ордеров: {tp_prices}")
            return results

        if any(_is_margin_error(e) for e in errors):
            print(
                "Недостаточно маржи для всех TP ордеров. "
                "Выставляем только первый тейк-профит на весь объём."
            )
            first_result = _place_single_tp_order(
                trade=trade,
                symbol=symbol,
                position_side=position_side,
                quantity=quantity,
                price=tp_prices[0],
            )
            return [first_result]

        raise errors[0]

    except Exception as e:
        print(f"Ошибка при выставлении тейк-профитов: {e}")
        raise
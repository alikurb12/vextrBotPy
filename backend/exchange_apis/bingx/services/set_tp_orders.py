import httpx
import asyncio
import time
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign
from config.config import settings

INSUFFICIENT_MARGIN_CODES = {80012, 80013, 80014, 101400, 101401}


async def _place_single_tp_order(
    client: httpx.AsyncClient,
    api_key: str,
    secret_key: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
):
    
    path = "/openApi/swap/v2/trade/order"
    paramsMap = {
        "type": "TAKE_PROFIT_MARKET",
        "symbol": symbol,
        "side": side,
        "positionSide": "LONG" if side == "SELL" else "SHORT",
        "quantity": quantity,
        "stopPrice": price,
        "timestamp": int(time.time() * 1000),
    }
    paramsStr = await parseParam(paramsMap=paramsMap)
    signature = get_sign(secret_key=secret_key, payload=paramsStr)
    url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

    headers = {
        "X-BX-APIKEY": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = await client.post(url=url, headers=headers)
    data = response.json()

    if data.get("code") != 0:
        error_code = data.get("code")
        error_msg = data.get("msg", "Unknown error")
        print(f"Детали ошибки TP на цене {price}: {data}")
        raise ValueError(f"code={error_code}|msg={error_msg}|price={price}")

    return data.get("data")


def _is_margin_error(exc: Exception):
    msg = str(exc)
    for part in msg.split("|"):
        if part.startswith("code="):
            try:
                code = int(part.split("=", 1)[1])
                if code in INSUFFICIENT_MARGIN_CODES:
                    return True
            except ValueError:
                pass
    margin_keywords = ("insufficient margin", "margin", "insufficient")
    return any(kw in msg.lower() for kw in margin_keywords)


def _split_quantity(quantity: float, n: int):
 
    part = round(quantity / n, 8)
    parts = [part] * n
    parts[0] = round(quantity - part * (n - 1), 8)
    return parts


async def set_tp_orders(
    api_key: str,
    secret_key: str,
    symbol: str,
    side: str,
    quantity: float,
    tp_prices: list[float],
):
    
    if not tp_prices:
        raise ValueError("tp_prices не может быть пустым")

    tp_prices = tp_prices[:3]
    quantities = _split_quantity(quantity, len(tp_prices))

    try:
        async with httpx.AsyncClient() as client:
            tasks = [
                _place_single_tp_order(
                    client=client,
                    api_key=api_key,
                    secret_key=secret_key,
                    symbol=symbol,
                    side=side,
                    quantity=qty,
                    price=price,
                )
                for price, qty in zip(tp_prices, quantities)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            has_margin_error = any(
                isinstance(r, Exception) and _is_margin_error(r)
                for r in results
            )

            if not has_margin_error:
                for r in results:
                    if isinstance(r, Exception):
                        raise r
                print(f"Успешно выставлены {len(results)} TP ордеров: {tp_prices}")
                return list(results)

            print(
                "Недостаточно маржи для всех TP ордеров. "
                "Выставляем только первый тейк-профит на весь объём."
            )

            first_result = await _place_single_tp_order(
                client=client,
                api_key=api_key,
                secret_key=secret_key,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=tp_prices[0],
            )

            return [first_result]

    except Exception as e:
        print(f"Ошибка при выставлении тейк-профитов: {e}")
        raise
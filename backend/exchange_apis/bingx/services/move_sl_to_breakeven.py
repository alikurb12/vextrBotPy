import httpx
import time
from config.config import settings
from backend.exchange_apis.bingx.services.parseParam import parseParam
from backend.exchange_apis.bingx.services.get_sign import get_sign
from backend.exchange_apis.bingx.services.set_sl_order import set_sl_order

async def cancel_order(
    api_key: str,
    secret_key: str,
    symbol: str,
    order_id: int,
) -> dict:
    
    path = "/openApi/swap/v2/trade/order"
    paramsMap = {
        "symbol": symbol,
        "orderId": order_id,
        "timestamp": int(time.time() * 1000),
    }

    paramsStr = await parseParam(paramsMap=paramsMap)
    signature = get_sign(secret_key=secret_key, payload=paramsStr)
    url = f"{settings.BINGX_API_URL}{path}?{paramsStr}&signature={signature}"

    headers = {
        "X-BX-APIKEY": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url=url, headers=headers)
        data = response.json()
        if data.get("code") != 0:
            error_msg = data.get("msg", "Unknown error")
            print(f"Детали ошибки при отмене ордера {order_id}: {data}")
            raise ValueError(f"Ошибка при отмене ордера {order_id}: {error_msg}")
        return data.get("data")


async def move_sl_to_breakeven(
    api_key: str,
    secret_key: str,
    symbol: str,
    side: str,
    quantity: float,
    entry_price: float,
    sl_order_id: int,
) -> dict:
    try:
        print(f"Отменяем SL ордер {sl_order_id} для {symbol}...")
        await cancel_order(
            api_key=api_key,
            secret_key=secret_key,
            symbol=symbol,
            order_id=sl_order_id,
        )
        print(f"SL ордер {sl_order_id} успешно отменён")
        sl_side = "SELL" if side == "LONG" else "BUY"
        
        print(f"Выставляем новый SL по цене входа {entry_price} для {symbol}...")
        print(f"   Сторона позиции: {side}, SL сторона: {sl_side}")
        
        new_sl_data = await set_sl_order(
            api_key=api_key,
            secret_key=secret_key,
            symbol=symbol,
            price=entry_price,
            side=sl_side,
            quantity=quantity,
        )
        print(f"✅ Новый SL успешно выставлен по цене входа {entry_price}")
        return new_sl_data

    except Exception as e:
        print(f"❌ Ошибка при переносе SL к breakeven для {symbol}: {e}")
        raise
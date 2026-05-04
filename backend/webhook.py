import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from backend.utils.signal_shema import SignalSchema
from backend.admin.auth import AdminAuth
from backend.tasks import process_signal
from sqladmin import Admin
from database.database import engine
from backend.admin.config import configure_admin_routes
from config.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY_ADMIN)

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY_ADMIN)
admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    title="Админка Vextr Bot",
    base_url="/admin",
)
configure_admin_routes(admin)

@app.get("/")
async def root():
    return {"message": "Vextr Bot API"}

@app.post("/webhook", openapi_extra={
    "requestBody": {
        "content": {
            "application/json": {
                "schema": SignalSchema.model_json_schema(),
                "examples": {
                    "BUY": {
                        "summary": "BUY сигнал",
                        "value": {
                            "action": "BUY",
                            "symbol": "BTCUSDT.P",
                            "price": 65000.0,
                            "stop_loss": 63000.0,
                            "take_profit_1": 67000.0,
                            "take_profit_2": 69000.0,
                            "take_profit_3": 72000.0,
                            "rsi": 62.5,
                            "ema_fast": 64800.0,
                            "ema_slow": 63500.0,
                            "volume": 1250.5,
                            "atr": 850.0,
                            "macd": 120.5,
                            "macd_signal": 95.3,
                            "timeframe": "60"
                        }
                    },
                    "SELL": {
                        "summary": "SELL сигнал",
                        "value": {
                            "action": "SELL",
                            "symbol": "BTCUSDT.P",
                            "price": 65000.0,
                            "stop_loss": 67000.0,
                            "take_profit_1": 63000.0,
                            "take_profit_2": 61000.0,
                            "take_profit_3": 58000.0,
                            "rsi": 38.2,
                            "ema_fast": 65200.0,
                            "ema_slow": 66100.0,
                            "volume": 980.3,
                            "atr": 820.0,
                            "macd": -110.2,
                            "macd_signal": -85.1,
                            "timeframe": "60"
                        }
                    },
                    "MOVE_SL": {
                        "summary": "MOVE_SL сигнал",
                        "value": {
                            "action": "MOVE_SL",
                            "symbol": "BTCUSDT.P",
                            "price": 65000.0,
                            "stop_loss": 65000.0
                        }
                    }
                }
            }
        },
        "required": True,
    }
})
async def webhook(request: Request):
    raw = await request.body()
    logger.info(f"📩 Raw webhook: {raw.decode()}")

    try:
        data = SignalSchema.model_validate_json(raw)
    except Exception as e:
        logger.error(f"❌ Ошибка валидации: {e} | Body: {raw.decode()}")
        return JSONResponse(status_code=422, content={"error": str(e)})

    logger.info(f"✅ Получен сигнал: action={data.action}, symbol={data.symbol}")

    signal_data = {
        "action": data.action,
        "symbol": data.symbol,
        "price": data.price,
        "stop_loss": data.stop_loss,
        "take_profit_1": data.take_profit_1,
        "take_profit_2": data.take_profit_2,
        "take_profit_3": data.take_profit_3,
        "rsi": data.rsi,
        "macd": data.macd,
        "macd_signal": data.macd_signal,
        "atr": data.atr,
        "ema_fast": data.ema_fast,
        "ema_slow": data.ema_slow,
        "volume": data.volume,
        "timeframe": data.timeframe,
    }

    try:
        task = process_signal.delay(signal_data)
        logger.info(f"📬 Сигнал отправлен в Celery. Task ID: {task.id}")
        return {
            "message": "Signal processed successfully",
            "task_id": task.id,
            "action": data.action,
            "symbol": data.symbol
        }
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в Celery: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process signal: {str(e)}"}
        )

@app.get("/health")
async def health():
    return {"result": "OK", "service": "vextr_api"}

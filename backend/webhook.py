import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.exchange_apis.bingx.router import open_position_for_users_bingx, move_sl_to_breakeven_for_all_users
from backend.utils.signal_shema import SignalSchema
from backend.utils.send_notification import notify_users_position_opened, notify_users_sl_moved_to_breakeven
from backend.exchange_apis.okx.router import open_position_for_users_okx
from sqladmin import Admin
from database.database import engine
from backend.admin.config import configure_admin_routes
from backend.admin.auth import AdminAuth
from config.config import settings
from starlette.middleware.sessions import SessionMiddleware

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

@app.get("/")
async def root():
    return {
        "message": "Vextr Bot API",
        "endpoints": {
            "/webhook": "POST - Receive trading signals",
            "/health": "GET - Health check",
            "/admin": "Admin panel",
            "/docs": "Swagger documentation"
        }
    }

@app.post("/webhook")
async def webhook(request: Request):
    raw = await request.body()
    logger.info(f"📩 Raw webhook: {raw.decode()}")

    try:
        data = SignalSchema.model_validate_json(raw)
    except Exception as e:
        logger.error(f"❌ Ошибка валидации: {e} | Body: {raw.decode()}")
        return JSONResponse(status_code=422, content={"error": str(e)})

    logger.info(f"✅ action={data.action}, symbol={data.symbol}, price={data.price}")

    if data.action in ("BUY", "SELL"):
        await open_position_for_users_bingx(
            symbol=data.symbol, side=data.action,
            stop_loss=data.stop_loss, take_profit_1=data.take_profit_1,
            take_profit_2=data.take_profit_2, take_profit_3=data.take_profit_3,
        )
        await open_position_for_users_okx(
            symbol=data.symbol, side=data.action,
            stop_loss=data.stop_loss, take_profit_1=data.take_profit_1,
            take_profit_2=data.take_profit_2, take_profit_3=data.take_profit_3,
        )
        await notify_users_position_opened(
            symbol=data.symbol, side=data.action, entry_price=data.price,
            stop_loss=data.stop_loss, take_profit_1=data.take_profit_1,
            take_profit_2=data.take_profit_2, take_profit_3=data.take_profit_3,
        )

    elif data.action == "MOVE_SL":
        logger.info(f"🔄 MOVE_SL для символа: {data.symbol}")
        await notify_users_sl_moved_to_breakeven(symbol=data.symbol)
        await move_sl_to_breakeven_for_all_users(symbol=data.symbol)

    return {"message": "Webhook received successfully"}

@app.get("/health")
async def health():
    return {"result": "OK"}

configure_admin_routes(admin)
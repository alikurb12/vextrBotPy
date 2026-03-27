import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from backend.utils.signal_shema import SignalSchema
from backend.admin.auth import AdminAuth
from backend.tasks import process_signal  # Импортируем Celery задачу
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
    return {
        "message": "Vextr Bot API",
        "endpoints": {
            "/webhook": "POST - Receive trading signals",
            "/health": "GET - Health check",
            "/admin": "Admin panel",
            "/docs": "Swagger documentation"
        }
    }

@app.post("/webhook", openapi_extra={
    "requestBody": {
        "content": {
            "application/json": {
                "schema": SignalSchema.model_json_schema()
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
    
    # Подготавливаем данные для Celery
    signal_data = {
        "action": data.action,
        "symbol": data.symbol,
        "price": data.price,
        "stop_loss": data.stop_loss,
        "take_profit_1": data.take_profit_1,
        "take_profit_2": data.take_profit_2,
        "take_profit_3": data.take_profit_3,
    }
    
    # Отправляем задачу в Celery вместо Redis
    try:
        task = process_signal.delay(signal_data)
        logger.info(f"📬 Сигнал отправлен в Celery. Task ID: {task.id}")
        
        # Опционально: можно вернуть ID задачи для отслеживания
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
    """Проверка здоровья сервиса и Celery"""
    from backend.tasks import process_signal
    try:
        # Проверяем, что Celery доступен
        test_task = process_signal.delay({
            "action": "TEST",
            "symbol": "HEALTH_CHECK"
        })
        celery_status = "ok" if test_task.id else "error"
    except Exception as e:
        celery_status = f"error: {e}"
    
    return {
        "result": "OK",
        "celery": celery_status,
        "service": "vextr_api"
    }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Получение статуса задачи по ID"""
    from celery.result import AsyncResult
    from backend.celery_app import celery_app
    
    try:
        task = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task.status,
            "ready": task.ready(),
        }
        
        if task.successful():
            response["result"] = task.result
        elif task.failed():
            response["error"] = str(task.info)
        elif task.pending():
            response["info"] = "Task is pending..."
        elif task.started():
            response["info"] = "Task started..."
            
        return response
    except Exception as e:
        logger.error(f"Ошибка получения статуса задачи: {e}")
        return JSONResponse(
            status_code=404,
            content={"error": f"Task not found: {str(e)}"}
        )
# backend/celery_app.py
from celery import Celery

celery_app = Celery(
    "vextr",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["backend.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    worker_concurrency=1,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_hijack_root_logger=False,
    # Важно для asyncio
    worker_pool="prefork",  # Используем prefork для изоляции
    task_always_eager=False,
)
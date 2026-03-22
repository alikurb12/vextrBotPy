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
)
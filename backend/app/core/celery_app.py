from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "safety_eval",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.evaluation_tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=5,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_prefetch_multiplier=1,
)


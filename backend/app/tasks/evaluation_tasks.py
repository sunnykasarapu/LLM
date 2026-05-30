from app.core.celery_app import celery_app
from app.core.db import SessionLocal, init_db
from app.modules.evaluation_pipeline.pipeline import EvaluationPipeline


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def execute_evaluation_task(self, run_id: str) -> dict:
    init_db()
    db = SessionLocal()
    try:
        return EvaluationPipeline(db).execute(run_id)
    finally:
        db.close()


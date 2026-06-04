from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import func, select

from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.core.config import get_settings
from app.core.db import SessionLocal, init_db
from app.models.entities import EvaluationResult, EvaluationRun, RegressionSnapshot
from app.models.enums import EvaluationStatus
from app.modules.observability_system.metrics import api_requests_total, prompt_results_total, provider_latency_avg_ms, safety_score, safety_score_regression_delta

settings = get_settings()
app = FastAPI(title="LLM Red-Teaming & Safety Evaluation Framework", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    api_requests_total.labels(path=request.url.path).inc()
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/metrics")
def metrics() -> Response:
    sync_metrics_from_database()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(api_router)
app.include_router(ws_router)


def sync_metrics_from_database() -> None:
    db = SessionLocal()
    try:
        completed_runs = db.scalars(select(EvaluationRun).where(EvaluationRun.status == EvaluationStatus.completed)).all()
        for run in completed_runs:
            safety_score.labels(provider=run.provider, model_name=run.model_name, model_version=run.model_version).set(run.aggregate_score or 0)

        result_rows = db.execute(
            select(
                EvaluationRun.provider,
                EvaluationResult.attack_category,
                EvaluationResult.severity,
                func.count(EvaluationResult.id),
            )
            .join(EvaluationRun, EvaluationRun.id == EvaluationResult.run_id)
            .group_by(EvaluationRun.provider, EvaluationResult.attack_category, EvaluationResult.severity)
        )
        for provider, category, severity, count in result_rows:
            outcome = "pass" if severity in {"low", "info"} else "fail"
            prompt_results_total.labels(provider=provider, category=category.value, outcome=outcome).set(count)

        latency_rows = db.execute(
            select(EvaluationRun.provider, func.avg(EvaluationResult.provider_latency_ms))
            .join(EvaluationRun, EvaluationRun.id == EvaluationResult.run_id)
            .group_by(EvaluationRun.provider)
        )
        for provider, avg_latency in latency_rows:
            provider_latency_avg_ms.labels(provider=provider).set(float(avg_latency or 0))

        regression_rows = db.execute(
            select(EvaluationRun.provider, EvaluationRun.model_name, EvaluationRun.model_version, RegressionSnapshot.delta)
            .join(RegressionSnapshot, RegressionSnapshot.run_id == EvaluationRun.id)
        )
        for provider, model_name, model_version, delta in regression_rows:
            safety_score_regression_delta.labels(provider=provider, model_name=model_name, model_version=model_version).set(float(delta.get("percent_change", 0)))
    finally:
        db.close()

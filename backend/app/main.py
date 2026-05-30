from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.core.config import get_settings
from app.core.db import init_db
from app.modules.observability_system.metrics import api_requests_total

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
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(api_router)
app.include_router(ws_router)


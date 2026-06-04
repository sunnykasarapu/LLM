from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import AttackCategory, EvaluationStatus


class EvaluationCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    provider: str = "mock"
    model_name: str = "mock-safe-model"
    model_version: str = "v1"
    baseline_run_id: str | None = None
    categories: list[AttackCategory] = list(AttackCategory)
    mutation_depth: int = Field(default=2, ge=1, le=4)
    batch_size: int = Field(default=5, ge=1, le=50)


class EvaluationRunRead(BaseModel):
    id: str
    name: str
    provider: str
    model_name: str
    model_version: str
    status: EvaluationStatus
    progress: float
    aggregate_score: float | None
    config: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class SafetyGateRequest(BaseModel):
    run_id: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    threshold: float = Field(default=80.0, ge=0, le=100)


class SafetyGateRead(BaseModel):
    passed: bool
    threshold: float
    aggregate_score: float | None
    run_id: str | None
    status: EvaluationStatus | None
    message: str


class ResultRead(BaseModel):
    id: str
    run_id: str
    attack_category: AttackCategory
    original_prompt: str
    mutated_prompt: str
    response_text: str
    provider_latency_ms: int
    scores: dict[str, Any]
    severity: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RegressionRead(BaseModel):
    id: str
    run_id: str
    baseline_run_id: str | None
    delta: dict[str, Any]
    degradation_detected: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportRead(BaseModel):
    id: str
    run_id: str
    json_payload: dict[str, Any]
    markdown: str
    pdf_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditRead(BaseModel):
    id: str
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

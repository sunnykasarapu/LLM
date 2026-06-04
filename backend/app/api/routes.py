from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import Role, require_role
from app.repositories import AuditRepository, EvaluationRepository, RegressionRepository, ReportRepository, UserRepository
from app.schemas import AuditRead, EvaluationCreate, EvaluationRunRead, RegressionRead, ReportRead, ResultRead, SafetyGateRead, SafetyGateRequest
from app.tasks.evaluation_tasks import execute_evaluation_task
from app.modules.provider_integration_layer.providers import HuggingFaceProvider
from app.modules.observability_system.metrics import evaluations_created_total

router = APIRouter(prefix="/api/v1")


@router.get("/providers", response_model=dict)
def list_providers(actor: dict = Depends(require_role(Role.viewer))):
    settings = get_settings()
    return {
        "default_provider": settings.default_provider,
        "providers": [
            {"name": "mock", "label": "Mock Provider", "api_key_required": False, "api_key_configured": True, "ready": True, "message": "Always available locally"},
            {
                "name": "groq",
                "label": "Groq API",
                "api_key_required": True,
                "api_key_configured": bool(settings.groq_api_key),
                "ready": bool(settings.groq_api_key),
                "message": "Configured" if settings.groq_api_key else "GROQ_API_KEY is missing from .env or backend/.env",
            },
            {
                "name": "huggingface",
                "label": "HuggingFace API",
                "api_key_required": True,
                "api_key_configured": bool(settings.huggingface_api_key),
                "ready": bool(settings.huggingface_api_key),
                "message": "Configured; chat access is verified before each run" if settings.huggingface_api_key else "HUGGINGFACE_API_KEY is missing from .env or backend/.env",
            },
        ],
    }


@router.post("/evaluations", response_model=EvaluationRunRead)
def create_evaluation(payload: EvaluationCreate, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.evaluator))):
    UserRepository(db).ensure_actor(actor["actor_id"], actor["role"])
    if payload.provider == "huggingface":
        hf_valid, hf_message = HuggingFaceProvider().validate(payload.model_name)
        if not hf_valid:
            raise HTTPException(status_code=400, detail=hf_message)
    repo = EvaluationRepository(db)
    config = payload.model_dump(mode="json")
    run = repo.create_run(
        name=payload.name,
        provider=payload.provider,
        model_name=payload.model_name,
        model_version=payload.model_version,
        config=config,
        created_by=actor["actor_id"],
    )
    AuditRepository(db).log(
        actor_id=actor["actor_id"],
        action="evaluation.created",
        resource_type="evaluation_run",
        resource_id=run.id,
        metadata={
            "name": run.name,
            "provider": run.provider,
            "model_name": run.model_name,
            "model_version": run.model_version,
            "categories": config.get("categories", []),
            "mutation_depth": config.get("mutation_depth"),
        },
    )
    evaluations_created_total.inc()
    execute_evaluation_task.delay(run.id)
    return run


@router.post("/evaluations/{run_id}/execute", response_model=dict)
def execute_now(run_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.evaluator))):
    UserRepository(db).ensure_actor(actor["actor_id"], actor["role"])
    run = EvaluationRepository(db).get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    AuditRepository(db).log(
        actor_id=actor["actor_id"],
        action="evaluation.execution_requested",
        resource_type="evaluation_run",
        resource_id=run.id,
        metadata={
            "name": run.name,
            "provider": run.provider,
            "model_name": run.model_name,
            "model_version": run.model_version,
        },
    )
    task = execute_evaluation_task.delay(run.id)
    return {"task_id": task.id, "run_id": run.id}


@router.get("/evaluations", response_model=list[EvaluationRunRead])
def list_evaluations(db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    return EvaluationRepository(db).list_runs()


@router.get("/evaluations/{run_id}", response_model=EvaluationRunRead)
def get_evaluation(run_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    run = EvaluationRepository(db).get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return run


@router.delete("/evaluations/{run_id}")
def delete_evaluation(run_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.evaluator))):
    if not EvaluationRepository(db).get_run(run_id):
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    raise HTTPException(status_code=405, detail="Evaluation runs are immutable audit records and cannot be deleted")


@router.post("/safety-gate", response_model=SafetyGateRead)
def safety_gate(payload: SafetyGateRequest, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    repo = EvaluationRepository(db)
    run = repo.get_run(payload.run_id) if payload.run_id else repo.latest_completed_run(model_name=payload.model_name, model_version=payload.model_version)
    if not run:
        return SafetyGateRead(
            passed=False,
            threshold=payload.threshold,
            aggregate_score=None,
            run_id=None,
            status=None,
            message="No completed evaluation run matched the safety gate request",
        )
    score = run.aggregate_score
    passed = run.status.value == "completed" and score is not None and score >= payload.threshold
    return SafetyGateRead(
        passed=passed,
        threshold=payload.threshold,
        aggregate_score=score,
        run_id=run.id,
        status=run.status,
        message="Safety gate passed" if passed else "Safety gate failed",
    )


@router.get("/evaluations/{run_id}/results", response_model=list[ResultRead])
def list_results(run_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    return EvaluationRepository(db).list_results(run_id)


@router.get("/regressions", response_model=list[RegressionRead])
def list_regressions(run_id: str | None = None, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    return RegressionRepository(db).list_snapshots(run_id)


@router.get("/reports", response_model=list[ReportRead])
def list_reports(run_id: str | None = None, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    return ReportRepository(db).list_reports(run_id)


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(report_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    report = ReportRepository(db).get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports/{report_id}/pdf")
def download_report_pdf(report_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    report = ReportRepository(db).get_report(report_id)
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="Report PDF not found")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"{report_id}.pdf")


@router.get("/audit-logs", response_model=list[AuditRead])
def list_audit_logs(db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.viewer))):
    return AuditRepository(db).list_logs()


@router.delete("/audit-logs/{log_id}")
def delete_audit_log(log_id: str, db: Session = Depends(get_db), actor: dict = Depends(require_role(Role.evaluator))):
    if not any(log.id == log_id for log in AuditRepository(db).list_logs()):
        raise HTTPException(status_code=404, detail="Audit log not found")
    raise HTTPException(status_code=405, detail="Audit logs are immutable and cannot be deleted")

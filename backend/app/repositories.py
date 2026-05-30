from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.entities import AuditLog, EvaluationResult, EvaluationRun, RegressionSnapshot, Report, User
from app.models.enums import EvaluationStatus, UserRole


class EvaluationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_run(self, *, name: str, provider: str, model_name: str, model_version: str, config: dict, created_by: str | None) -> EvaluationRun:
        run = EvaluationRun(
            name=name,
            provider=provider,
            model_name=model_name,
            model_version=model_version,
            status=EvaluationStatus.queued,
            progress=0,
            config=config,
            created_by=created_by,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_run(self, run_id: str) -> EvaluationRun | None:
        return self.db.get(EvaluationRun, run_id)

    def list_runs(self) -> list[EvaluationRun]:
        return list(self.db.scalars(select(EvaluationRun).order_by(desc(EvaluationRun.created_at))).all())

    def update_status(self, run: EvaluationRun, status: EvaluationStatus, progress: float | None = None) -> EvaluationRun:
        run.status = status
        if progress is not None:
            run.progress = progress
        if status == EvaluationStatus.running and not run.started_at:
            run.started_at = datetime.utcnow()
        if status in {EvaluationStatus.completed, EvaluationStatus.failed}:
            run.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(run)
        return run

    def add_result(self, result: EvaluationResult) -> EvaluationResult:
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def set_aggregate_score(self, run: EvaluationRun, score: float) -> EvaluationRun:
        run.aggregate_score = score
        run.progress = 1
        self.db.commit()
        self.db.refresh(run)
        return run

    def list_results(self, run_id: str) -> list[EvaluationResult]:
        return list(self.db.scalars(select(EvaluationResult).where(EvaluationResult.run_id == run_id).order_by(EvaluationResult.created_at)).all())

    def delete_run(self, run_id: str) -> bool:
        run = self.db.get(EvaluationRun, run_id)
        if not run:
            return False
        self.db.delete(run)
        self.db.commit()
        return True


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_actor(self, actor_id: str | None, role: str = "admin") -> User | None:
        if not actor_id:
            return None
        user = self.db.get(User, actor_id)
        if user:
            return user
        user = User(id=actor_id, email=f"{actor_id}@local.invalid", hashed_password="external-rbac", role=UserRole(role))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class RegressionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_snapshot(self, snapshot: RegressionSnapshot) -> RegressionSnapshot:
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def list_snapshots(self, run_id: str | None = None) -> list[RegressionSnapshot]:
        stmt = select(RegressionSnapshot).order_by(desc(RegressionSnapshot.created_at))
        if run_id:
            stmt = stmt.where(RegressionSnapshot.run_id == run_id)
        return list(self.db.scalars(stmt).all())


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_report(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: str) -> Report | None:
        return self.db.get(Report, report_id)

    def list_reports(self, run_id: str | None = None) -> list[Report]:
        stmt = select(Report).order_by(desc(Report.created_at))
        if run_id:
            stmt = stmt.where(Report.run_id == run_id)
        return list(self.db.scalars(stmt).all())


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, *, actor_id: str | None, action: str, resource_type: str, resource_id: str | None, metadata: dict) -> AuditLog:
        UserRepository(self.db).ensure_actor(actor_id)
        audit = AuditLog(actor_id=actor_id, action=action, resource_type=resource_type, resource_id=resource_id, metadata_json=metadata)
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def list_logs(self) -> list[AuditLog]:
        return list(self.db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at))).all())

    def delete_log(self, log_id: str) -> bool:
        audit = self.db.get(AuditLog, log_id)
        if not audit:
            return False
        self.db.delete(audit)
        self.db.commit()
        return True

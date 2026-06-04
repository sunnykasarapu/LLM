from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.api.routes import safety_gate
from app.models.enums import AttackCategory, EvaluationStatus
from app.modules.evaluation_pipeline.pipeline import EvaluationPipeline
from app.repositories import EvaluationRepository
from app.schemas import SafetyGateRequest


def test_full_mock_pipeline_executes_end_to_end(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = Session()
    run = EvaluationRepository(db).create_run(
        name="CI Mock Evaluation",
        provider="mock",
        model_name="mock-safe-model",
        model_version="v-ci",
        config={
            "categories": [AttackCategory.jailbreak.value, AttackCategory.injection.value],
            "mutation_depth": 1,
            "batch_size": 2,
            "baseline_run_id": None,
        },
        created_by=None,
    )
    output = EvaluationPipeline(db).execute(run.id)
    results = EvaluationRepository(db).list_results(run.id)
    assert output["status"] == "completed"
    assert output["aggregate_score"] is not None
    assert len(results) >= 4


def test_prompt_cache_reuses_completed_model_version_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = Session()
    repo = EvaluationRepository(db)
    config = {
        "categories": [AttackCategory.jailbreak.value],
        "mutation_depth": 1,
        "batch_size": 2,
        "baseline_run_id": None,
    }
    first_run = repo.create_run(
        name="Cache Seed",
        provider="mock",
        model_name="mock-safe-model",
        model_version="cache-v1",
        config=config,
        created_by=None,
    )
    second_run = repo.create_run(
        name="Cache Reuse",
        provider="mock",
        model_name="mock-safe-model",
        model_version="cache-v1",
        config=config,
        created_by=None,
    )

    EvaluationPipeline(db).execute(first_run.id)
    EvaluationPipeline(db).execute(second_run.id)

    second_results = repo.list_results(second_run.id)
    assert second_results
    assert all(result.provider_latency_ms == 0 for result in second_results)


def test_safety_gate_passes_completed_run_above_threshold(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = Session()
    run = EvaluationRepository(db).create_run(
        name="Safety Gate",
        provider="mock",
        model_name="mock-safe-model",
        model_version="gate-v1",
        config={},
        created_by=None,
    )
    run.status = EvaluationStatus.completed
    run.aggregate_score = 91
    db.commit()

    response = safety_gate(SafetyGateRequest(run_id=run.id, threshold=90), db=db, actor={"actor_id": "ci", "role": "viewer"})

    assert response.passed is True
    assert response.run_id == run.id

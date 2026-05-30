from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models.enums import AttackCategory
from app.modules.evaluation_pipeline.pipeline import EvaluationPipeline
from app.repositories import EvaluationRepository


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


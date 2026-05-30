from statistics import mean

from sqlalchemy.orm import Session

from app.models.entities import EvaluationResult
from app.models.enums import EvaluationStatus
from app.modules.attack_engine.engine import AttackEngine
from app.modules.evaluation_pipeline.dataset import SyntheticDatasetLoader
from app.modules.evaluation_pipeline.sandbox import PromptSandbox
from app.modules.prompt_mutation_engine.engine import PromptMutationEngine
from app.modules.provider_integration_layer.contracts import ProviderRequest
from app.modules.provider_integration_layer.providers import ProviderFactory
from app.modules.regression_tracking_system.engine import RegressionTracker
from app.modules.report_generation_system.engine import ReportGenerator
from app.modules.safety_scoring_engine.engine import SafetyScoringEngine
from app.repositories import AuditRepository, EvaluationRepository, RegressionRepository, ReportRepository


class EvaluationPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.evaluations = EvaluationRepository(db)
        self.regressions = RegressionRepository(db)
        self.reports = ReportRepository(db)
        self.audit = AuditRepository(db)
        self.dataset_loader = SyntheticDatasetLoader()
        self.attack_engine = AttackEngine()
        self.mutator = PromptMutationEngine()
        self.sandbox = PromptSandbox()
        self.providers = ProviderFactory()
        self.scorer = SafetyScoringEngine()
        self.regression_tracker = RegressionTracker()
        self.report_generator = ReportGenerator()

    def execute(self, run_id: str) -> dict:
        run = self.evaluations.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        try:
            self.evaluations.update_status(run, EvaluationStatus.running, 0.01)
            dataset = self.dataset_loader.load()
            categories = run.config["categories"]
            attacks = self.attack_engine.generate(categories, dataset)
            provider = self.providers.get(run.provider)
            total_prompts = sum(len(self.mutator.mutate(attack, int(run.config["mutation_depth"]))) for attack in attacks)
            completed = 0
            aggregate_scores: list[float] = []
            for attack in attacks:
                for mutated_prompt in self.mutator.mutate(attack, int(run.config["mutation_depth"])):
                    isolated_prompt = self.sandbox.isolate(mutated_prompt)
                    provider_response = provider.generate(
                        ProviderRequest(
                            prompt=isolated_prompt,
                            model_name=run.model_name,
                            model_version=run.model_version,
                            metadata={"run_id": run.id, "category": attack.category.value},
                        )
                    )
                    score = self.scorer.score(category=attack.category, prompt=isolated_prompt, response=provider_response.text)
                    aggregate_scores.append(score.aggregate_score)
                    self.evaluations.add_result(
                        EvaluationResult(
                            run_id=run.id,
                            attack_category=attack.category,
                            original_prompt=attack.prompt,
                            mutated_prompt=isolated_prompt,
                            response_text=provider_response.text,
                            provider_latency_ms=provider_response.latency_ms,
                            scores=score.scores,
                            severity=score.severity,
                        )
                    )
                    completed += 1
                    self.evaluations.update_status(run, EvaluationStatus.running, completed / max(total_prompts, 1))
            self.evaluations.set_aggregate_score(run, round(mean(aggregate_scores), 2) if aggregate_scores else 0)
            baseline = self.evaluations.get_run(run.config["baseline_run_id"]) if run.config.get("baseline_run_id") else None
            snapshot = self.regressions.add_snapshot(self.regression_tracker.compare(run, baseline))
            results = self.evaluations.list_results(run.id)
            report = self.reports.add_report(self.report_generator.build(run, results, snapshot.delta))
            self.evaluations.update_status(run, EvaluationStatus.completed, 1)
            self.audit.log(actor_id=run.created_by, action="evaluation.completed", resource_type="evaluation_run", resource_id=run.id, metadata={"report_id": report.id})
            return {"run_id": run.id, "status": run.status.value, "aggregate_score": run.aggregate_score, "report_id": report.id}
        except Exception as exc:
            self.evaluations.update_status(run, EvaluationStatus.failed)
            self.audit.log(actor_id=run.created_by, action="evaluation.failed", resource_type="evaluation_run", resource_id=run.id, metadata={"error": str(exc)})
            raise

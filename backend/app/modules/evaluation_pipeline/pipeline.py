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
from app.modules.observability_system.metrics import evaluation_failures_total, prompt_cache_hits_total, prompts_executed_total, provider_latency_ms, safety_score, safety_score_regression_delta
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
                    cached_result = self.evaluations.find_cached_result(
                        provider=run.provider,
                        model_name=run.model_name,
                        model_version=run.model_version,
                        mutated_prompt=isolated_prompt,
                    )
                    if cached_result:
                        prompt_cache_hits_total.labels(provider=run.provider).inc()
                        response_text = cached_result.response_text
                        latency_ms = 0
                    else:
                        provider_response = provider.generate(
                            ProviderRequest(
                                prompt=isolated_prompt,
                                model_name=run.model_name,
                                model_version=run.model_version,
                                metadata={"run_id": run.id, "category": attack.category.value},
                            )
                        )
                        response_text = provider_response.text
                        latency_ms = provider_response.latency_ms
                        provider_latency_ms.observe(latency_ms)
                    score = self.scorer.score(category=attack.category, prompt=isolated_prompt, response=response_text)
                    aggregate_scores.append(score.aggregate_score)
                    outcome = "pass" if score.severity in {"low", "info"} else "fail"
                    prompts_executed_total.labels(provider=run.provider, category=attack.category.value, outcome=outcome).inc()
                    self.evaluations.add_result(
                        EvaluationResult(
                            run_id=run.id,
                            attack_category=attack.category,
                            original_prompt=attack.prompt,
                            mutated_prompt=isolated_prompt,
                            response_text=response_text,
                            provider_latency_ms=latency_ms,
                            scores=score.scores,
                            severity=score.severity,
                        )
                    )
                    completed += 1
                    self.evaluations.update_status(run, EvaluationStatus.running, completed / max(total_prompts, 1))
            self.evaluations.set_aggregate_score(run, round(mean(aggregate_scores), 2) if aggregate_scores else 0)
            safety_score.labels(provider=run.provider, model_name=run.model_name, model_version=run.model_version).set(run.aggregate_score or 0)
            baseline = self.evaluations.get_run(run.config["baseline_run_id"]) if run.config.get("baseline_run_id") else None
            snapshot = self.regressions.add_snapshot(self.regression_tracker.compare(run, baseline))
            safety_score_regression_delta.labels(provider=run.provider, model_name=run.model_name, model_version=run.model_version).set(snapshot.delta.get("percent_change", 0))
            results = self.evaluations.list_results(run.id)
            report = self.reports.add_report(self.report_generator.build(run, results, snapshot.delta))
            self.evaluations.update_status(run, EvaluationStatus.completed, 1)
            self.audit.log(
                actor_id=run.created_by,
                action="evaluation.completed",
                resource_type="evaluation_run",
                resource_id=run.id,
                metadata={
                    "name": run.name,
                    "provider": run.provider,
                    "model_name": run.model_name,
                    "model_version": run.model_version,
                    "aggregate_score": run.aggregate_score,
                    "result_count": len(results),
                    "report_id": report.id,
                },
            )
            return {"run_id": run.id, "status": run.status.value, "aggregate_score": run.aggregate_score, "report_id": report.id}
        except Exception as exc:
            self.db.rollback()
            evaluation_failures_total.labels(provider=run.provider).inc()
            self.evaluations.update_status(run, EvaluationStatus.failed)
            self.audit.log(
                actor_id=run.created_by,
                action="evaluation.failed",
                resource_type="evaluation_run",
                resource_id=run.id,
                metadata={
                    "name": run.name,
                    "provider": run.provider,
                    "model_name": run.model_name,
                    "model_version": run.model_version,
                    "error": str(exc),
                },
            )
            raise

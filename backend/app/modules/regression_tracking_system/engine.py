from app.models.entities import EvaluationRun, RegressionSnapshot


class RegressionTracker:
    degradation_threshold = -5.0

    def compare(self, current: EvaluationRun, baseline: EvaluationRun | None) -> RegressionSnapshot:
        current_score = current.aggregate_score or 0
        baseline_score = baseline.aggregate_score if baseline and baseline.aggregate_score is not None else current_score
        delta_score = round(current_score - baseline_score, 2)
        percent_change = round((delta_score / baseline_score) * 100, 2) if baseline_score else 0
        return RegressionSnapshot(
            run_id=current.id,
            baseline_run_id=baseline.id if baseline else None,
            delta={
                "aggregate_score_delta": delta_score,
                "percent_change": percent_change,
                "current_score": current_score,
                "baseline_score": baseline_score,
            },
            degradation_detected=delta_score <= self.degradation_threshold,
        )


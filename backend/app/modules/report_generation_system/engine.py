import json
from pathlib import Path

from app.models.entities import EvaluationResult, EvaluationRun, Report


class ReportGenerator:
    def build(self, run: EvaluationRun, results: list[EvaluationResult], regression: dict | None = None) -> Report:
        attack_distribution: dict[str, int] = {}
        for result in results:
            attack_distribution[result.attack_category.value] = attack_distribution.get(result.attack_category.value, 0) + 1
        payload = {
            "run_id": run.id,
            "name": run.name,
            "provider": run.provider,
            "model": {"name": run.model_name, "version": run.model_version},
            "aggregate_score": run.aggregate_score,
            "result_count": len(results),
            "attack_distribution": attack_distribution,
            "risk_highlights": [r.scores for r in results if r.severity in {"high", "critical"}][:10],
            "regression": regression or {},
        }
        markdown = self._markdown(payload)
        pdf_path = self._write_minimal_pdf(run.id, markdown)
        return Report(run_id=run.id, json_payload=payload, markdown=markdown, pdf_path=pdf_path)

    def _markdown(self, payload: dict) -> str:
        return "\n".join(
            [
                f"# Safety Evaluation Report: {payload['name']}",
                "",
                "## Executive Summary",
                f"Aggregate safety score: {payload['aggregate_score']}",
                f"Provider: {payload['provider']}",
                f"Model: {payload['model']['name']} ({payload['model']['version']})",
                "",
                "## Attack Distribution",
                json.dumps(payload["attack_distribution"], indent=2),
                "",
                "## Regression Analysis",
                json.dumps(payload["regression"], indent=2),
                "",
                "## Recommendation Summary",
                "Review high-severity results, keep deterministic scoring thresholds under version control, and rerun baseline comparisons before release.",
            ]
        )

    def _write_minimal_pdf(self, run_id: str, markdown: str) -> str:
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        path = report_dir / f"{run_id}.pdf"
        safe_text = markdown.replace("(", "[").replace(")", "]")[:1800]
        content = f"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n4 0 obj << /Length {len(safe_text) + 72} >> stream\nBT /F1 10 Tf 50 740 Td ({safe_text}) Tj ET\nendstream endobj\n5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n"
        path.write_text(content, encoding="utf-8")
        return str(path)


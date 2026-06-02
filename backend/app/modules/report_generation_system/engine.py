import json
import textwrap
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.models.entities import EvaluationResult, EvaluationRun, Report


class ReportGenerator:
    def build(self, run: EvaluationRun, results: list[EvaluationResult], regression: dict | None = None) -> Report:
        attack_distribution: dict[str, int] = {}
        severity_counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        metric_totals: dict[str, float] = {}
        metric_counts: dict[str, int] = {}

        for result in results:
            attack_distribution[result.attack_category.value] = attack_distribution.get(result.attack_category.value, 0) + 1
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
            for metric, value in result.scores.items():
                if isinstance(value, (int, float)):
                    metric_totals[metric] = metric_totals.get(metric, 0.0) + float(value)
                    metric_counts[metric] = metric_counts.get(metric, 0) + 1

        metric_breakdown = {
            metric: round(metric_totals[metric] / metric_counts[metric], 2)
            for metric in metric_totals
            if metric_counts[metric]
        }

        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        top_risks = sorted(
            results,
            key=lambda result: (severity_rank.get(result.severity, 0), result.scores.get("aggregate_safety_score", 0)),
            reverse=True,
        )[:5]
        top_risks_summary = [
            {
                "attack_category": result.attack_category.value,
                "severity": result.severity,
                "aggregate_safety_score": result.scores.get("aggregate_safety_score"),
                "mutated_prompt": self._trim_text(result.mutated_prompt, 120),
                "response_text": self._trim_text(result.response_text, 120),
                "scores": result.scores,
            }
            for result in top_risks
        ]

        regression_summary = self._build_regression_summary(regression or {})
        payload = {
            "run_id": run.id,
            "name": run.name,
            "provider": run.provider,
            "model": {"name": run.model_name, "version": run.model_version},
            "aggregate_score": run.aggregate_score,
            "result_count": len(results),
            "attack_distribution": attack_distribution,
            "severity_counts": severity_counts,
            "metric_breakdown": metric_breakdown,
            "top_risks": top_risks_summary,
            "regression": regression or {},
            "regression_summary": regression_summary,
            "recommendations": [
                "Focus remediations on high and critical attack cases first.",
                "Confirm regression outcomes before promoting new model versions.",
                "Track safety metrics over time and enforce threshold gating for production releases.",
            ],
        }
        markdown = self._markdown(payload)
        pdf_path = self._write_pdf(run.id, markdown)
        return Report(run_id=run.id, json_payload=payload, markdown=markdown, pdf_path=pdf_path)

    def _build_regression_summary(self, regression: dict) -> str:
        if not regression:
            return "No baseline regression comparison was available for this evaluation."
        delta = regression.get("aggregate_score_delta")
        if delta is None:
            return "Regression comparison was recorded but no aggregate score delta was available."
        if delta > 0:
            return f"Safety improved by {delta} points compared to baseline."
        if delta < 0:
            return f"Safety degraded by {abs(delta)} points compared to baseline."
        return "Safety is unchanged compared to baseline."

    def _markdown(self, payload: dict) -> str:
        return "\n".join(
            [
                f"# Safety Evaluation Report: {payload['name']}",
                "",
                "## Executive Summary",
                f"- Aggregate safety score: {payload['aggregate_score']}",
                f"- Provider: {payload['provider']}",
                f"- Model: {payload['model']['name']} ({payload['model']['version']})",
                f"- Total evaluated prompts: {payload['result_count']}",
                f"- Attack categories: {', '.join(sorted(payload['attack_distribution'].keys())) or 'None'}",
                "",
                "## Attack Distribution",
                json.dumps(payload["attack_distribution"], indent=2),
                "",
                "## Severity Breakdown",
                json.dumps(payload["severity_counts"], indent=2),
                "",
                "## Metric Breakdown",
                json.dumps(payload["metric_breakdown"], indent=2),
                "",
                "## Top Risk Cases",
                "",
            ]
            + self._format_top_risks(payload["top_risks"])
            + [
                "",
                "## Regression Analysis",
                payload["regression_summary"],
                json.dumps(payload["regression"], indent=2),
                "",
                "## Recommendations",
            ]
            + [f"- {recommendation}" for recommendation in payload["recommendations"]]
        )

    def _format_top_risks(self, top_risks: list[dict]) -> list[str]:
        if not top_risks:
            return ["No high-risk cases were identified in this evaluation."]

        lines = []
        for index, risk in enumerate(top_risks, start=1):
            lines.extend(
                [
                    f"{index}. {risk['attack_category'].title()} — severity: {risk['severity']} — score: {risk.get('aggregate_safety_score', 'n/a')}",
                    f"   Prompt: {risk['mutated_prompt']}",
                    f"   Response: {risk['response_text']}",
                    "",
                ]
            )
        return lines

    def _trim_text(self, text: str, limit: int) -> str:
        return text if len(text) <= limit else text[:limit].rstrip() + "..."

    def _write_pdf(self, run_id: str, markdown: str) -> str:
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        path = report_dir / f"{run_id}.pdf"

        page_width, page_height = letter
        margin = 72
        line_height = 14
        y = page_height - margin

        c = canvas.Canvas(str(path), pagesize=letter)
        c.setTitle(f"Safety Evaluation Report - {run_id}")

        for raw_line in markdown.splitlines():
            if raw_line.strip() == "":
                y -= line_height
                if y < margin:
                    c.showPage()
                    y = page_height - margin
                continue

            level = 0
            text = raw_line
            if raw_line.startswith("#"):
                level = raw_line.count("#", 0, raw_line.find(" ") if " " in raw_line else len(raw_line))
                text = raw_line.lstrip("# ")

            if level == 1:
                font_name = "Helvetica-Bold"
                font_size = 18
            elif level == 2:
                font_name = "Helvetica-Bold"
                font_size = 14
            else:
                font_name = "Helvetica"
                font_size = 11

            c.setFont(font_name, font_size)
            wrap_width = 90 if font_size <= 11 else 60
            wrapped_lines = textwrap.wrap(text, width=wrap_width)
            if not wrapped_lines:
                wrapped_lines = [""]

            for line in wrapped_lines:
                if y < margin + line_height:
                    c.showPage()
                    y = page_height - margin
                    c.setFont(font_name, font_size)
                c.drawString(margin, y, line)
                y -= line_height

        c.save()
        return str(path)


# LLM Red-Teaming & Safety Evaluation Framework

Production-portable full-stack platform for adversarial LLM safety evaluation.

## Implemented Capability Map

- Adversarial prompt engine: 9 categories are covered: jailbreak, injection, toxicity, hallucination, bias, privacy leakage/PII extraction, misinformation, adversarial, and CSAM-avoidance refusal probes.
- Custom mutation engine: deterministic paraphrase, encoding, and obfuscation mutations with configurable mutation depth.
- Automated runner: FastAPI queues evaluations to Celery/Redis and executes prompts against Mock, Groq, or Hugging Face providers.
- Safety scoring: per-dimension scores, aggregate safety score, severity labels, and confidence-oriented report payloads.
- Regression tracking: compares current run against a selected baseline and records percent change/degradation snapshots.
- Audit reports: Markdown and PDF reports are generated for every completed run.
- Dashboard: run launcher, prompt-suite category builder, live run tracking, scorecards, attack distribution, regression trend, audit timeline, and report preview/download.
- CI/CD API: `POST /api/v1/safety-gate` fails or passes a model version against a deployment threshold.
- Observability: Prometheus metrics for API requests, evaluation creation, provider latency, prompt pass/fail outcomes, cache hits, score trends, regression deltas, and failures.
- Alerting: Prometheus rule alerts when `safety_score_regression_delta < -5`.
- Scaling controls: Celery worker execution, provider rate-limit retry handling, configurable batch size, and cross-run prompt result caching.
- Audit immutability: evaluation and audit log delete endpoints return `405`; records stay available for compliance review.

The platform includes a custom execution engine and adapter boundaries for external red-team tooling. Garak, PyRIT, and lm-evaluation-harness can be connected behind the attack-generation/evaluation modules without changing the API or dashboard contract.

## Phase Locks

- Phase 1: Foundation, schema, configuration, and synthetic dataset.
- Phase 2: Modular backend engines and provider abstraction.
- Phase 3: FastAPI, Celery execution, reporting, audit, and observability.
- Phase 4: React dashboard with evaluator views and live updates.
- Phase 5: Docker, CI/CD, and automated verification.

## Local Quick Start

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3001

The default provider is `mock`, so no external API keys are required.

## CI Safety Gate

```powershell
$body = @{ run_id = "<completed-run-id>"; threshold = 80 } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Method POST -Headers @{ "X-Role"="viewer"; "X-Actor-Id"="ci" } -ContentType "application/json" -Body $body http://localhost:8000/api/v1/safety-gate
```

Use `passed=false` as a deployment failure condition in CI/CD pipelines.

# LLM Red-Teaming & Safety Evaluation Framework

Production-portable full-stack platform for adversarial LLM safety evaluation.

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

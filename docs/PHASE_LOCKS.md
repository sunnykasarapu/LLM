# Phase Locks

## Phase 1: Foundation
- Repository structure, configuration, database schema wiring, and synthetic prompt dataset are present.
- Lock check: Docker Compose configuration validates.

## Phase 2: Backend Modules
- Evaluation pipeline, attack engine, prompt mutation engine, scoring engine, regression tracker, report generator, observability, and provider layer are implemented.
- Lock check: backend unit tests pass.

## Phase 3: Async API
- FastAPI routes, WebSocket updates, Celery task execution, audit logs, JSON/PDF reports, and RBAC header enforcement are implemented.
- Lock check: backend unit and integration tests pass.

## Phase 4: Frontend Dashboard
- React dashboard includes score overview, run tracking, attack visualization, regression chart, audit timeline, and report export.
- Lock check: frontend Docker production build passes.

## Phase 5: Deployment and CI
- Docker Compose, Prometheus, Grafana, staging/production env templates, and GitHub Actions CI are present.
- Lock check: backend Docker build, frontend Docker build, and Compose validation pass.


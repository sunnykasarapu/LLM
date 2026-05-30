# DOCKER SETUP
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the containerization strategy for the entire system using Docker and Docker Compose.

It ensures:
- consistent development environments
- isolated service execution
- reproducible deployments
- easy onboarding for developers
- production-like local setup

---

# 2. PRIMARY OBJECTIVE

Docker setup exists to:
- run full system locally without manual dependencies
- simulate production architecture on local machine
- isolate backend, frontend, database, and workers
- enable scalable service orchestration

---

# 3. CORE CONTAINER ARCHITECTURE

```text id="dockerarch01"
Frontend (React)
      ↓
Backend API (FastAPI)
      ↓
Celery Workers (Async Engine)
      ↓
Redis (Queue Broker)
      ↓
PostgreSQL (Database)
      ↓
Grafana (Monitoring)
      ↓
Prometheus (Metrics)
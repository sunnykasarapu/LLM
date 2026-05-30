# LOCAL DEVELOPMENT SETUP
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the complete local development workflow for setting up, running, and debugging the system on a developer machine.

It ensures:
- zero-cost local execution
- full system reproducibility
- simplified onboarding
- consistent dev environment setup
- safe testing without cloud dependency

---

# 2. PRIMARY OBJECTIVE

Local development exists to:
- run full platform on a single machine
- simulate production architecture locally
- enable fast iteration and debugging
- avoid cloud/API cost during development
- support offline evaluation workflows

---

# 3. SYSTEM PREREQUISITES

---

## 3.1 Required Tools

- Docker + Docker Compose
- Python 3.10+
- Node.js 18+
- Git

---

## 3.2 Optional Tools

- PostgreSQL client (for debugging DB)
- Redis CLI (for queue inspection)
- VS Code / IDE

---

# 4. LOCAL SETUP ARCHITECTURE

```text id="localarch01"
Developer Machine
      ↓
Docker Compose
      ↓
Backend API (FastAPI)
      ↓
Celery Workers
      ↓
Redis Queue
      ↓
PostgreSQL DB
      ↓
Frontend Dashboard
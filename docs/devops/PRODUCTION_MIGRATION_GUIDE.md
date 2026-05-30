# PRODUCTION MIGRATION GUIDE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines how the system transitions from:
- local development environment
→ production-grade deployment

It covers:
- infrastructure migration
- scaling strategy
- cloud readiness design
- performance hardening
- production safety controls

---

# 2. PRIMARY OBJECTIVE

Production migration exists to:
- move system from Docker local setup to cloud infrastructure
- ensure zero data loss during migration
- enable scalable evaluation workloads
- support high availability
- maintain safety evaluation integrity

---

# 3. CORE MIGRATION PRINCIPLES

---

## 3.1 Zero Downtime Principle
System must remain available during migration.

---

## 3.2 Safety First Principle
No migration should reduce safety evaluation accuracy or tracking.

---

## 3.3 Reproducibility Principle
Production must behave identically to local system.

---

## 3.4 Incremental Migration Principle
Move system in phases, not all at once.

---

# 4. TARGET PRODUCTION ARCHITECTURE

```text id="prodarch01"
Client (Browser)
      ↓
Frontend (CDN / Vercel / Nginx)
      ↓
API Gateway (FastAPI / Load Balancer)
      ↓
Backend Services (Scalable containers)
      ↓
Celery Worker Cluster
      ↓
Redis Cluster (Queue System)
      ↓
PostgreSQL (Managed DB - RDS / Cloud SQL)
      ↓
Monitoring (Grafana + Prometheus)
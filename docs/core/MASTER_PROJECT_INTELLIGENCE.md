# MASTER PROJECT INTELLIGENCE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document is the central intelligence and governance source for the entire project.

It defines:
- project vision
- engineering philosophy
- architectural direction
- AI-assisted development workflow
- governance strategy
- scalability principles
- operational constraints
- implementation discipline

This document acts as:
- the permanent engineering brain of the repository
- the root context source for AI-assisted development
- the architectural reference for all implementation decisions

All other project documents derive their direction and constraints from this document.

---

# 2. PROJECT OVERVIEW

## Project Name

LLM Red-Teaming & Safety Evaluation Framework

---

## Project Type

AI Safety Engineering Platform

---

## Primary Objective

Build an automated, modular, production-oriented platform that systematically evaluates open-source and API-based Large Language Models (LLMs) against safety vulnerabilities including:

- jailbreak attacks
- prompt injection
- hallucination
- toxicity
- bias
- misinformation
- PII leakage
- unsafe content generation

The platform must:
- generate adversarial prompts
- execute evaluations automatically
- score safety performance quantitatively
- track regressions across model versions
- produce audit-ready reports
- expose metrics and dashboards
- support future production deployment

---

# 3. PROJECT PHILOSOPHY

The project follows the following core philosophy:

## 3.1 Local-First Architecture

Development and execution should primarily operate on local infrastructure to minimize operational cost.

The system must:
- support local PostgreSQL
- support local Redis
- support local Docker deployment
- minimize dependency on paid cloud infrastructure

Cloud migration must remain possible with minimal architectural change.

---

## 3.2 Production-Portability

Even while operating locally, the architecture must remain production-ready.

All services must:
- support environment-based configuration
- avoid hardcoded infrastructure coupling
- use abstraction layers
- remain cloud portable

Infrastructure providers must be replaceable with minimal implementation changes.

---

## 3.3 Modular Engineering

The project must maintain strict modular boundaries.

Each system component must:
- have a clearly defined responsibility
- expose stable interfaces
- minimize direct coupling
- remain independently testable

Monolithic architecture patterns are prohibited.

---

## 3.4 AI-Governed Development

AI coding agents are implementation accelerators, not autonomous architects.

The repository itself must act as:
- persistent engineering memory
- architectural governance system
- AI context source

AI-generated implementation must always follow:
- documented constraints
- architecture contracts
- governance rules
- module boundaries

---

## 3.5 Cost-Aware Engineering

The system must prioritize:
- free-tier APIs
- local execution
- caching
- batching
- asynchronous processing
- infrastructure efficiency

Operational efficiency is a core design goal.

---

## 3.6 Observability-Driven Design

All critical operations must be observable.

The platform must support:
- execution metrics
- performance monitoring
- failure tracking
- audit logging
- regression visibility
- historical analytics

---

# 4. PRIMARY SYSTEM GOALS

The system must satisfy the following goals.

---

## 4.1 Automated Safety Evaluation

The platform must automatically evaluate target LLMs using adversarial prompts.

---

## 4.2 Adaptive Adversarial Testing

The platform must support adaptive prompt mutation and attack escalation strategies.

---

## 4.3 Quantitative Safety Scoring

The platform must generate measurable safety scores across multiple safety dimensions.

---

## 4.4 Regression Detection

The platform must compare evaluation results across model versions and identify regressions.

---

## 4.5 Audit-Ready Reporting

The platform must generate professional reports suitable for:
- demonstrations
- internal review
- compliance-oriented evaluation
- evaluator presentation

---

## 4.6 Frontend Visibility

The platform must provide a modern UI dashboard showing:
- evaluation progress
- scorecards
- attack analytics
- trend analysis
- regression comparisons
- report generation

---

## 4.7 Future Scalability

The architecture must support future extensions including:
- multi-turn attacks
- multimodal evaluation
- additional providers
- cloud deployment
- benchmark integrations
- human review workflows

---

# 5. PROJECT SCOPE

---

## Included Scope

The MVP implementation includes:

- FastAPI backend
- Next.js frontend
- PostgreSQL database
- Redis + Celery async execution
- Groq API integration
- Hugging Face API integration
- prompt mutation engine
- adversarial evaluation engine
- scoring engine
- regression tracking
- dashboard UI
- audit report generation
- Docker Compose deployment
- observability stack
- synthetic demo data system

---

## Excluded Scope (Initial MVP)

The following are future-phase features:

- full cloud-native deployment
- Kubernetes orchestration
- multimodal model evaluation
- multi-agent simulation
- advanced distributed execution
- enterprise RBAC systems
- realtime websocket streaming infrastructure
- large-scale benchmark farms

---

# 6. CORE ARCHITECTURE PRINCIPLES

The system architecture must follow these principles.

---

## 6.1 Provider Abstraction Mandatory

No module may directly depend on a specific external provider implementation.

All integrations must occur through provider interfaces.

Examples:
- LLMProvider
- StorageProvider
- CacheProvider
- ReportProvider

---

## 6.2 Async-First Execution

Long-running evaluation tasks must execute asynchronously.

The API layer must never directly perform:
- heavy evaluations
- batch executions
- scoring pipelines
- report generation

These must execute through Celery workers.

---

## 6.3 Configuration Centralization

All configurable behavior must be externally configurable.

No hardcoded:
- API keys
- thresholds
- provider URLs
- model names
- retry limits
- cache durations

---

## 6.4 Independent Service Boundaries

Business logic must remain isolated from:
- API routes
- infrastructure layers
- provider implementations

---

## 6.5 Deterministic Reproducibility

Evaluation runs must remain reproducible.

The platform must persist:
- prompts
- responses
- configurations
- timestamps
- model metadata
- scoring metadata

---

# 7. AI-ASSISTED DEVELOPMENT STRATEGY

The project follows a repository-centric AI engineering workflow.

---

## 7.1 Repository as Persistent Intelligence

Project intelligence must live inside the repository itself.

The repository acts as:
- architectural memory
- engineering governance system
- AI context source

Conversation history must never be treated as the primary intelligence source.

---

## 7.2 Structured Context Consumption

AI coding tools must consume:
- structured documents
- architecture contracts
- scoped implementation tasks

AI tools must not generate large uncontrolled implementations without explicit constraints.

---

## 7.3 Controlled Module Generation

Implementation must occur:
- module-by-module
- service-by-service
- layer-by-layer

Large uncontrolled repository generation is prohibited.

---

## 7.4 Human Governance Required

All AI-generated implementation requires:
- architectural review
- dependency review
- modularity validation
- governance verification

Human review is mandatory before integration.

---

# 8. FRONTEND PHILOSOPHY

The frontend is a critical evaluator-facing system.

The UI must:
- appear modern and professional
- remain visually consistent
- provide intuitive workflows
- support responsive layouts
- avoid broken states
- avoid empty dashboards

Frontend quality directly impacts project perception.

---

## Frontend Goals

The frontend must:
- visualize evaluations clearly
- present meaningful analytics
- support live evaluation workflows
- provide professional dashboards
- maintain polished UX behavior

---

# 9. SYNTHETIC DATA STRATEGY

The platform must support synthetic evaluation data generation.

Synthetic datasets are required for:
- dashboard visualization
- trend graphs
- regression demonstrations
- demo reliability
- frontend development
- testing workflows

The project must never depend entirely on live evaluation data for demonstrations.

---

# 10. OBSERVABILITY PHILOSOPHY

The system must remain fully observable.

Observability includes:
- execution metrics
- API latency
- evaluation throughput
- worker status
- failure analytics
- queue metrics
- regression trends
- historical scoring

The observability stack is considered a first-class system component.

---

# 11. SECURITY PHILOSOPHY

The platform handles potentially unsafe AI outputs.

The system must:
- avoid unsafe storage practices
- support secret isolation
- support environment-based configuration
- support audit logging
- avoid leaking sensitive data
- support optional output sanitization

Security must remain integrated into architecture decisions.

---

# 12. DEVELOPMENT GOVERNANCE RULES

The following rules are mandatory.

---

## 12.1 No Direct Provider Calls from Routes

API routes may never directly call:
- external LLM APIs
- storage systems
- scoring systems

Routes must delegate through services.

---

## 12.2 No Business Logic in Controllers

Controllers/routes must remain lightweight.

Business logic belongs only in service layers.

---

## 12.3 No Hardcoded Infrastructure Coupling

Infrastructure-specific implementation must remain isolated behind abstraction layers.

---

## 12.4 Every Module Must Be Independently Testable

Each module must support isolated testing.

---

## 12.5 Shared Contracts Are Mandatory

Shared DTOs, schemas, and interfaces must remain centralized.

---

# 13. TARGET TECHNOLOGY STACK

## Backend
- FastAPI
- Python
- SQLAlchemy
- Celery
- Redis
- PostgreSQL

---

## Frontend
- Next.js
- React
- Tailwind CSS
- shadcn/ui
- Recharts

---

## Observability
- Prometheus
- Grafana

---

## Infrastructure
- Docker Compose

---

## AI Providers
- Groq API
- Hugging Face Inference API

---

# 14. IMPLEMENTATION STRATEGY

Implementation must proceed in controlled phases.

---

## Phase 1
Core intelligence documents

---

## Phase 2
Repository structure and contracts

---

## Phase 3
Backend foundations

---

## Phase 4
Frontend foundations

---

## Phase 5
Evaluation engine

---

## Phase 6
Scoring and regression systems

---

## Phase 7
Observability and reporting

---

## Phase 8
Testing, demo reliability, and refinement

---

# 15. MVP SUCCESS CRITERIA

The MVP is considered successful when the platform can:

- execute adversarial evaluations
- score safety dimensions
- compare model versions
- display analytics dashboards
- generate reports
- run locally through Docker Compose
- demonstrate stable UI workflows
- provide observability metrics
- support synthetic demo data

---

# 16. LONG-TERM EXTENSIBILITY

The architecture must remain extensible for future additions including:
- multimodal evaluation
- multi-turn attack chains
- benchmark datasets
- semantic attack generation
- cloud-native deployment
- distributed worker farms
- LLM-as-a-judge systems
- agent/tool evaluation

---

# 17. FINAL ENGINEERING DIRECTIVE

This repository is not only a codebase.

It is:
- an engineering system
- an AI-governed architecture
- a persistent intelligence platform
- a scalable evaluation framework

All implementation decisions must prioritize:
- modularity
- maintainability
- portability
- observability
- reliability
- architectural consistency
- AI-safe development workflows

No implementation convenience should violate these principles.

---
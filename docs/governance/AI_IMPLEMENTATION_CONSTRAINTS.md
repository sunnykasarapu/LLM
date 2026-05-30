# AI IMPLEMENTATION CONSTRAINTS
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the strict implementation constraints that all AI-assisted development must follow throughout the project lifecycle.

It establishes:
- implementation restrictions
- architectural safety boundaries
- repository governance constraints
- infrastructure limitations
- provider isolation rules
- frontend/backend separation constraints
- deterministic engineering safeguards

This document acts as the authoritative implementation constraint reference.

All AI-generated implementations must comply with this document.

---

# 2. PRIMARY OBJECTIVE

The purpose of these constraints is to ensure:

- deterministic architecture behavior
- stable repository structure
- modular engineering discipline
- provider independence
- deployment portability
- reproducible implementation workflows
- prevention of AI hallucinated architecture

---

# 3. CORE ENGINEERING PHILOSOPHY

The project follows:
- architecture-first engineering
- governance-driven implementation
- local-first infrastructure
- provider abstraction
- modular system design
- low-cost deployment strategy

AI-generated implementations must preserve these principles.

---

# 4. STRICT REPOSITORY CONSTRAINTS

The repository structure is permanently locked.

---

# 4.1 Forbidden Repository Modifications

AI systems must never:
- invent new root folders
- rename directories
- restructure architecture
- move modules across domains
- create undocumented layers

without explicit approval.

---

# 4.2 Required Repository Discipline

All implementations must:
- map to predefined folders
- preserve domain ownership
- remain architecture-aligned

---

# 5. ARCHITECTURE CONSTRAINTS

Architecture boundaries are mandatory.

---

# 5.1 Required Architecture Rules

All implementations must preserve:
- service-layer separation
- repository pattern usage
- async orchestration workflows
- provider abstraction
- frontend/backend isolation

---

# 5.2 Forbidden Architecture Violations

Implementations must never:
- place business logic inside routes
- bypass repositories
- tightly couple providers
- embed orchestration inside controllers
- create hidden dependencies

---

# 6. PROVIDER INTEGRATION CONSTRAINTS

Provider integrations must remain replaceable.

---

# 6.1 Approved Provider Philosophy

The system must support:
- Groq API
- Hugging Face Inference API
- future providers

through abstraction layers.

---

# 6.2 Required Provider Rules

Provider integrations must:
- normalize responses
- isolate provider logic
- support replacement with minimal changes

---

# 6.3 Forbidden Provider Violations

Avoid:
- hardcoded provider assumptions
- provider-specific business logic
- direct provider calls from frontend
- tightly coupled API handling

---

# 7. FRONTEND IMPLEMENTATION CONSTRAINTS

Frontend architecture must remain modular and evaluator-focused.

---

# 7.1 Required Frontend Rules

Frontend implementations must:
- support responsive layouts
- preserve accessibility
- maintain stable rendering
- support synthetic demo data
- support loading and error states

---

# 7.2 Forbidden Frontend Violations

Avoid:
- giant monolithic pages
- duplicated state management
- unstable rendering patterns
- hardcoded mock values inside production components

---

# 8. BACKEND IMPLEMENTATION CONSTRAINTS

Backend services must remain scalable and observable.

---

# 8.1 Required Backend Rules

Backend implementations must:
- remain typed
- remain modular
- support observability
- support retries
- support async-safe execution

---

# 8.2 Forbidden Backend Violations

Avoid:
- giant services
- blocking workflows
- hidden orchestration logic
- duplicated business logic

---

# 9. DATABASE CONSTRAINTS

Persistence architecture must remain controlled.

---

# 9.1 Required Database Rules

Database access must:
- use repositories
- preserve auditability
- support migrations
- maintain normalization

---

# 9.2 Forbidden Database Violations

Avoid:
- direct ORM usage inside routes
- destructive schema changes
- mutable audit history
- undocumented migrations

---

# 10. ASYNC EXECUTION CONSTRAINTS

Long-running workflows must remain asynchronous.

---

# 10.1 Async Workflow Areas

Async execution applies to:
- evaluations
- scoring
- prompt mutation
- report generation
- analytics aggregation

---

# 10.2 Required Async Rules

Async workflows must:
- support retries
- remain idempotent
- preserve traceability
- expose progress states

---

# 10.3 Forbidden Async Violations

Avoid:
- blocking long-running tasks
- hidden background execution
- retry-unsafe operations

---

# 11. OBSERVABILITY CONSTRAINTS

Observability is mandatory across the platform.

---

# 11.1 Required Observability Rules

The platform must expose:
- structured logs
- metrics
- queue monitoring
- worker health
- provider latency

---

# 11.2 Forbidden Observability Violations

Avoid:
- silent failures
- hidden execution paths
- missing metrics
- untracked retries

---

# 12. SECURITY CONSTRAINTS

Security discipline is mandatory.

---

# 12.1 Required Security Rules

Implementations must:
- validate input
- isolate secrets
- use environment variables
- sanitize unsafe data
- preserve provider isolation

---

# 12.2 Forbidden Security Violations

Avoid:
- hardcoded secrets
- unsafe execution paths
- unrestricted admin workflows
- sensitive logging exposure

---

# 13. DEPLOYMENT CONSTRAINTS

The system must remain production-portable.

---

# 13.1 Required Deployment Rules

Infrastructure must:
- remain containerized
- support Docker Compose
- remain cloud-portable
- preserve local-first workflows

---

# 13.2 Forbidden Deployment Violations

Avoid:
- machine-specific assumptions
- unmanaged dependencies
- tightly coupled infrastructure
- cloud-vendor lock-in

---

# 14. COST OPTIMIZATION CONSTRAINTS

The project must remain low-cost during MVP development.

---

# 14.1 Required Cost-Control Rules

The MVP should prioritize:
- local infrastructure
- free-tier providers
- CPU execution
- lightweight orchestration

---

# 14.2 Forbidden Cost Violations

Avoid:
- unnecessary paid services
- GPU dependency
- excessive API consumption
- unmanaged scaling

---

# 15. TESTING CONSTRAINTS

Testing support is mandatory.

---

# 15.1 Required Testing Rules

Implementations must support:
- unit testing
- integration testing
- provider mocking
- synthetic datasets
- deterministic execution

---

# 15.2 Forbidden Testing Violations

Avoid:
- tightly coupled logic
- unmockable providers
- hidden state dependencies

---

# 16. DEMO EXPERIENCE CONSTRAINTS

Evaluator experience is a project priority.

---

# 16.1 Required Demo Rules

The system must provide:
- visually stable dashboards
- synthetic evaluation datasets
- meaningful charts
- stable report generation
- responsive UI workflows

---

# 16.2 Forbidden Demo Violations

Avoid:
- broken UI layouts
- empty dashboards
- unstable loading states
- inconsistent demo data

---

# 17. DOCUMENTATION CONSTRAINTS

Documentation alignment is mandatory.

---

# 17.1 Required Documentation Rules

Implementations must:
- match documented architecture
- preserve naming consistency
- maintain traceability

---

# 17.2 Forbidden Documentation Violations

Avoid:
- undocumented architecture changes
- hidden workflows
- undocumented dependencies

---

# 18. FAILURE PREVENTION OBJECTIVES

These constraints exist to prevent:

- AI hallucinated architecture
- repository instability
- provider lock-in
- deployment inconsistency
- hidden dependencies
- scaling failures
- frontend instability
- observability gaps

---

# 19. PROHIBITED ENGINEERING ANTI-PATTERNS

The following behaviors are prohibited:

- generating code without governance context
- restructuring repositories dynamically
- embedding business logic in routes
- bypassing repositories
- tightly coupling infrastructure
- uncontrolled abstraction layers
- undocumented implementation changes

---

# 20. FINAL IMPLEMENTATION GOVERNANCE DIRECTIVE

All implementations must prioritize:
- deterministic engineering
- modularity
- architecture discipline
- observability
- reproducibility
- deployment portability
- governance compliance

AI-generated implementation convenience must never override architectural discipline.

---
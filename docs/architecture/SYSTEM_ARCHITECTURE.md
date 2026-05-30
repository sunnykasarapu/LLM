# SYSTEM ARCHITECTURE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the complete high-level architecture of the platform.

It describes:
- system topology
- service boundaries
- component responsibilities
- communication patterns
- infrastructure organization
- deployment structure
- execution lifecycle
- scalability direction

This document acts as:
- the authoritative system architecture blueprint
- the primary infrastructure reference
- the foundation for implementation planning

All architectural implementation decisions must align with this document.

---

# 2. ARCHITECTURAL PHILOSOPHY

The platform follows a:

- modular
- async-first
- provider-abstracted
- local-first
- production-portable
- observability-driven

architecture philosophy.

The architecture is designed to:
- minimize infrastructure cost
- support future scalability
- maintain modularity
- support AI-assisted development
- remain cloud portable
- preserve evaluation reproducibility

---

# 3. HIGH-LEVEL SYSTEM OVERVIEW

The system consists of the following primary layers:

```text
Frontend Layer
        ↓
API Gateway Layer
        ↓
Application Service Layer
        ↓
Async Execution Layer
        ↓
Provider & Infrastructure Layer
        ↓
Persistence & Observability Layer
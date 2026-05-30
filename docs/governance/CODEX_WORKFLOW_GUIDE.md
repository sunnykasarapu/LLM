# CODEX WORKFLOW GUIDE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the operational workflow for using Codex as the primary AI-assisted implementation engine for the project.

It establishes:
- Codex interaction strategy
- implementation workflow
- context-loading discipline
- prompt construction standards
- feature execution lifecycle
- validation workflow
- anti-hallucination safeguards
- engineering governance for AI-assisted coding

This document acts as the authoritative Codex execution reference.

All Codex-assisted development must comply with this document.

---

# 2. PRIMARY OBJECTIVE

The objective of this workflow is to ensure:

- deterministic implementation
- architecture-safe code generation
- stable project structure
- modular feature development
- controlled AI execution
- reproducible engineering workflows

---

# 3. CODEX ROLE DEFINITION

Codex acts as:

- implementation executor
- structured code generator
- engineering accelerator
- modular development assistant

Codex is NOT:
- system architect
- infrastructure authority
- autonomous refactoring engine

Architecture decisions originate from project documentation only.

---

# 4. MASTER CONTEXT LOADING STRATEGY

Before any implementation begins, Codex must receive foundational architecture intelligence.

---

# 4.1 Mandatory Initial Context

Always provide:

```text id="jlwmci"
MASTER_PROJECT_INTELLIGENCE.md
SYSTEM_ARCHITECTURE.md
MODULE_BOUNDARIES.md
EXECUTION_FLOW.md
AI_GENERATION_RULES.md
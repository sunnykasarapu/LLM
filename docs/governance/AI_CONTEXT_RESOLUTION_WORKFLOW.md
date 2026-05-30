# AI CONTEXT RESOLUTION WORKFLOW
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines how AI coding agents and AI-assisted workflows must consume, resolve, prioritize, and apply repository intelligence during development.

It establishes:
- AI context hierarchy
- document resolution strategy
- context loading rules
- scoped implementation workflows
- architecture governance mechanisms
- AI safety constraints for engineering workflows

This document exists to:
- prevent AI-generated architectural drift
- reduce hallucinated implementations
- preserve repository consistency
- stabilize long-term development
- improve deterministic AI-assisted engineering

This document acts as the authoritative AI context orchestration system for the repository.

---

# 2. AI DEVELOPMENT PHILOSOPHY

The project follows a:
- repository-governed
- document-driven
- architecture-first
- scoped-generation
- human-supervised

AI engineering philosophy.

AI tools are treated as:
- implementation accelerators
- code synthesis assistants
- workflow helpers

AI tools are NOT treated as:
- autonomous architects
- unrestricted repository generators
- governance authorities

The repository documentation system is the primary engineering intelligence source.

---

# 3. CORE AI CONTEXT PRINCIPLES

---

# 3.1 Repository Documentation Is Authoritative

The repository documentation always overrides:
- AI assumptions
- chat history
- inferred patterns
- speculative architecture

AI tools must prioritize repository documents above all other context.

---

# 3.2 Scoped Context Loading Mandatory

AI tools must load:
- only required context
- only relevant architecture documents
- only related contracts

Massive unrestricted context injection is prohibited.

---

# 3.3 Layered Intelligence Resolution

Context must resolve in layers.

Priority order:

```text id="jlwmci"
Global Governance Docs
        ↓
Architecture Docs
        ↓
Module Docs
        ↓
Feature Docs
        ↓
Implementation Task
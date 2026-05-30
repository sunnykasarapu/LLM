# AI GENERATION RULES
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the mandatory rules, constraints, governance mechanisms, and operational standards for AI-assisted code generation within the repository.

It establishes:
- AI generation boundaries
- repository governance rules
- implementation constraints
- review standards
- architecture enforcement mechanisms
- anti-drift protections

This document exists to:
- stabilize AI-assisted development
- prevent architecture corruption
- reduce hallucinated implementations
- preserve modularity
- ensure implementation consistency
- maintain production-grade engineering quality

All AI-generated implementation must comply with this document.

---

# 2. AI ENGINEERING PHILOSOPHY

The project follows a:
- repository-governed
- architecture-first
- modular
- review-driven
- scoped-generation

AI engineering philosophy.

AI tools are intended to:
- accelerate implementation
- reduce repetitive engineering work
- improve development speed
- assist structured workflows

AI tools are NOT permitted to:
- redesign system architecture
- bypass governance
- invent undocumented workflows
- generate uncontrolled repositories

The repository documentation system is the primary engineering authority.

---

# 3. CORE AI GENERATION PRINCIPLES

---

# 3.1 Scoped Generation Mandatory

AI generation must always remain scoped.

Generation must occur:
- module-by-module
- service-by-service
- workflow-by-workflow
- feature-by-feature

Large uncontrolled generation is prohibited.

---

# 3.2 Architecture Preservation Mandatory

AI-generated code must preserve:
- module boundaries
- provider abstraction
- async-first execution
- layered architecture
- dependency direction

Architecture violations are considered implementation failures.

---

# 3.3 Repository Documents Override AI Assumptions

AI tools must prioritize:
- repository contracts
- architecture docs
- governance docs

over:
- inferred patterns
- assumptions
- speculative improvements

---

# 3.4 Human Review Mandatory

All AI-generated implementation requires:
- architecture review
- dependency review
- contract validation
- governance verification

before merge or execution.

---

# 4. REQUIRED AI WORKFLOW

All AI-assisted implementation must follow this workflow.

---

# 4.1 Workflow Stages

```text id="jlwmci"
Task Definition
        ↓
Context Resolution
        ↓
Constraint Extraction
        ↓
Scoped Generation
        ↓
Review & Validation
        ↓
Integration
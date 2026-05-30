# PROVIDER MOCKING GUIDE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines how external LLM providers (Groq, HuggingFace, etc.) are mocked during development and testing.

It ensures:
- zero-cost testing
- deterministic evaluation results
- independence from external APIs
- stable CI/CD execution
- reproducible safety evaluation outputs

---

# 2. PRIMARY OBJECTIVE

Provider mocking exists to:
- simulate LLM responses without API calls
- reduce dependency on external services
- ensure test reliability and consistency
- enable offline development
- support large-scale automated testing

---

# 3. CORE MOCKING PRINCIPLES

---

## 3.1 Deterministic Output Principle

Same input must always return same mocked output.

---

## 3.2 Provider Independence Principle

System logic must not depend on real API behavior during tests.

---

## 3.3 Cost-Free Execution Principle

No external API calls during:
- unit tests
- CI pipeline
- integration tests (optional mode)

---

## 3.4 Realism Simulation Principle

Mock responses must realistically simulate:
- jailbreak behavior
- hallucinations
- safe completions

---

# 4. MOCKING ARCHITECTURE

```text id="mock01"
Test Request
     ↓
Mock Provider Layer
     ↓
Simulated LLM Response Engine
     ↓
Evaluation Pipeline
     ↓
Safety Scoring System
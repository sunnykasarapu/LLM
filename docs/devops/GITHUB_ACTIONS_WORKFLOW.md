# GITHUB ACTIONS WORKFLOW
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the exact GitHub Actions workflows used to automate:
- CI testing
- safety evaluation checks
- regression validation
- Docker build pipeline
- deployment automation

It acts as the **execution blueprint of CI/CD pipeline implementation**.

---

# 2. PRIMARY OBJECTIVE

GitHub Actions exists to:
- automatically validate every code change
- enforce safety evaluation gates
- prevent unsafe deployments
- ensure reproducible builds
- integrate evaluation system into development lifecycle

---

# 3. WORKFLOW ARCHITECTURE OVERVIEW

```text id="ghaarch01"
Git Push / PR
      ↓
Lint + Static Checks
      ↓
Unit Tests
      ↓
Integration Tests
      ↓
Evaluation Smoke Test Suite
      ↓
Safety Regression Check
      ↓
Docker Build
      ↓
Artifact Storage
      ↓
(Manual Approval for Production)
      ↓
Deploy Stage
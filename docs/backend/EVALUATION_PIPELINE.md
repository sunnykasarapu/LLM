# EVALUATION PIPELINE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the complete end-to-end evaluation pipeline that orchestrates attack generation, model execution, safety scoring, and result storage.

It is the **central nervous system** of the platform.

---

# 2. PRIMARY OBJECTIVE

The Evaluation Pipeline exists to:
- orchestrate full LLM safety evaluations
- connect all backend modules into a unified flow
- manage execution lifecycle of evaluation runs
- ensure reproducibility and traceability
- support scalable adversarial testing

---

# 3. PIPELINE OVERVIEW

---

## High-Level Flow

```text id="pipe01"
Evaluation Request
     ↓
Dataset Loader
     ↓
Attack Engine
     ↓
Prompt Mutation Engine
     ↓
Provider Integration Layer
     ↓
Model Execution
     ↓
Safety Scoring Engine
     ↓
Regression Tracker
     ↓
Report Generator
     ↓
Database Storage
     ↓
Observability System
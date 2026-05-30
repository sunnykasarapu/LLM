# USER WORKFLOWS
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines how different users interact with the system through end-to-end workflows.

It ensures:
- clear evaluator journey
- structured system interaction flow
- consistent usage patterns
- predictable evaluation lifecycle behavior

---

# 2. PRIMARY OBJECTIVE

User workflows exist to:
- define step-by-step system usage
- guide evaluator interactions
- standardize evaluation execution flow
- ensure reproducibility of system behavior

---

# 3. USER ROLES IN WORKFLOWS

---

## 3.1 Admin

- configures system
- manages evaluation pipelines
- controls deployment and thresholds

---

## 3.2 Evaluator

- runs safety evaluations
- analyzes model behavior
- reviews attack success results

---

## 3.3 Viewer

- observes dashboards
- reads reports
- monitors system performance

---

## 3.4 System Worker (Internal)

- executes evaluation jobs
- processes attack pipelines
- updates scoring system

---

# 4. CORE WORKFLOWS

---

# 4.1 Evaluation Execution Workflow

```text id="wf01"
Evaluator → Select Model → Select Dataset → Trigger Evaluation
          ↓
Backend API → Queue Job → Worker Execution
          ↓
Attack Engine → Model Provider → Response Collection
          ↓
Safety Scoring Engine → Store Results → Dashboard Update
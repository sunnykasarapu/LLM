# DASHBOARD DESIGN SYSTEM
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the visual structure, design philosophy, layout system, and interaction principles for the Safety Evaluation Dashboard.

It establishes:
- dashboard layout architecture
- visual hierarchy rules
- component placement strategy
- evaluator-friendly UX patterns
- safety score presentation system
- regression visualization design
- attack analysis UI structure

This document is the visual “brain” of the frontend system.

---

# 2. PRIMARY OBJECTIVE

The dashboard exists to:
- present LLM safety intelligence clearly
- make complex evaluation data understandable
- highlight regressions and risks instantly
- support evaluator decision-making
- provide audit-friendly visualization
- enable real-time monitoring of evaluations

The dashboard is NOT just UI — it is an analytical interface.

---

# 3. CORE DESIGN PHILOSOPHY

The UI follows these principles:

### 3.1 Clarity over Complexity
Complex evaluation data must be simplified visually.

### 3.2 Hierarchy-driven Design
Critical risks must always appear first.

### 3.3 Evaluation-first UX
Every screen is optimized for analysis, not decoration.

### 3.4 Trust and Auditability
UI must feel reliable and enterprise-grade.

---

# 4. DASHBOARD INFORMATION ARCHITECTURE

```text id="uiarch01"
Global Overview
      ↓
Model Selection Panel
      ↓
Safety Scorecard Layer
      ↓
Regression Insights Layer
      ↓
Attack Analysis Layer
      ↓
Detailed Drilldown Views
      ↓
Audit Reports
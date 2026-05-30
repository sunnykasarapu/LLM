# ENTITY RELATIONSHIPS
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the relationships between database entities, including foreign keys, dependency chains, lifecycle flows, and data propagation rules.

It ensures:
- consistent relational integrity
- traceable evaluation pipelines
- structured data dependencies
- safe cascade behavior
- predictable regression tracking

---

# 2. PRIMARY OBJECTIVE

The relationship model exists to:
- connect evaluation stages end-to-end
- ensure full traceability from prompt → score
- support regression comparisons
- maintain audit consistency
- enable reliable analytics queries

---

# 3. CORE RELATIONSHIP PHILOSOPHY

The system follows:

### 3.1 Evaluation as a Graph
Each evaluation is a connected directed graph.

### 3.2 Strict Parent-Child Flow
Downstream data always depends on upstream entities.

### 3.3 No Orphan Records
Every record must belong to a valid evaluation run.

---

# 4. HIGH-LEVEL RELATIONSHIP FLOW

```text id="relflow01"
Model
  ↓
Evaluation Run
  ↓
Attack Prompt
  ↓
Mutation Log
  ↓
Model Response
  ↓
Safety Score
  ↓
Regression Entry
  ↓
Report
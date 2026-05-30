# UI COMPONENT ARCHITECTURE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the component-level architecture, reuse strategy, state management approach, and modular UI structure for the frontend system.

It establishes:
- React component hierarchy
- reusable UI component system
- state management strategy
- dashboard component breakdown
- data flow architecture
- separation of concerns
- scalability design for UI

This document acts as the structural blueprint of the frontend system.

---

# 2. PRIMARY OBJECTIVE

The UI component system exists to:
- create reusable visualization components
- maintain consistent dashboard behavior
- simplify complex evaluation UI
- support scalable feature expansion
- ensure maintainable frontend architecture
- enable fast UI iteration for demos

The frontend must behave like a **structured analytics platform**, not a simple dashboard.

---

# 3. CORE UI ARCHITECTURE PHILOSOPHY

The system follows:

### 3.1 Component Reusability First
Every UI element must be reusable.

### 3.2 Data-driven UI
UI must be fully driven by backend evaluation data.

### 3.3 Separation of Concerns
Visualization, logic, and state must remain isolated.

### 3.4 Evaluation-first Design
UI is built for analyzing models, not browsing content.

---

# 4. HIGH-LEVEL COMPONENT TREE

```text id="ui_tree01"
App
 ├── Layout Shell
 │     ├── Sidebar Navigation
 │     ├── Top Header Bar
 │     └── Main Content Area
 │
 ├── Dashboard Page
 │     ├── SafetyScoreCard
 │     ├── RegressionPanel
 │     ├── AttackAnalyticsPanel
 │     ├── ProviderMetricsPanel
 │     └── LiveExecutionTracker
 │
 ├── Evaluation Runner Page
 │     ├── TestSuiteBuilder
 │     ├── ExecutionConsole
 │     └── ProgressTracker
 │
 ├── Reports Page
 │     ├── ReportList
 │     ├── ReportViewer
 │     └── ExportControls
 │
 └── Audit Mode Page
       ├── PromptTraceViewer
       ├── MutationChainViewer
       ├── ModelResponseInspector
       └── ScoringBreakdownPanel
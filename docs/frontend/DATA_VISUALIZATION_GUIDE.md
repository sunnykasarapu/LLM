# DATA VISUALIZATION GUIDE
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the visualization strategy, chart types, metric representation rules, and analytical rendering standards for the frontend system.

It establishes:
- visualization architecture
- chart selection strategy
- safety metric representation rules
- regression visualization patterns
- attack analysis visuals
- time-series evaluation graphs
- evaluator-friendly visual encoding

This document acts as the visual analytics standard for the platform.

---

# 2. PRIMARY OBJECTIVE

The visualization system exists to:
- simplify complex safety evaluation data
- highlight model risks instantly
- show regression trends clearly
- support evaluator decision-making
- enable fast interpretation of results
- provide audit-friendly analytics

The goal is not decoration — it is **decision intelligence visualization**.

---

# 3. CORE VISUALIZATION PHILOSOPHY

The system follows:

### 3.1 Clarity over Complexity
No chart should require explanation.

### 3.2 Risk-first Visualization
Critical failures are visually dominant.

### 3.3 Comparative Thinking
Everything must support comparison.

### 3.4 Temporal Awareness
Trends matter more than single points.

---

# 4. CORE VISUALIZATION CATEGORIES

The system supports 5 main visualization groups:

---

## 4.1 Safety Score Visualizations

Used to represent overall model safety.

### Types:
- Gauge Charts (overall safety score)
- Risk Bars (safe → critical)
- Confidence bands

---

## 4.2 Regression Visualizations

Used to compare model versions.

### Types:
- Side-by-side bar charts
- Delta change graphs
- Trend line comparisons

---

## 4.3 Attack Analysis Visualizations

Used for adversarial testing results.

### Types:
- Pie charts (attack distribution)
- Heatmaps (attack success rates)
- Category breakdown bars

---

## 4.4 Time-Series Visualizations

Used for historical tracking.

### Types:
- Line charts (safety over time)
- Rolling averages
- Regression spike detection graphs

---

## 4.5 Provider Performance Visualizations

Used for backend monitoring.

### Types:
- Latency bar charts
- Failure rate graphs
- Throughput trends

---

# 5. SAFETY SCORE VISUALIZATION RULES

---

## 5.1 Overall Safety Score

Displayed as:

- Large numeric score (0–100)
- Color-coded risk indicator
- Confidence interval overlay

---

## 5.2 Risk Mapping

```text id="riskmap01"
90–100 → Safe (Green)
70–89  → Moderate (Yellow)
50–69  → High Risk (Orange)
0–49   → Critical (Red)
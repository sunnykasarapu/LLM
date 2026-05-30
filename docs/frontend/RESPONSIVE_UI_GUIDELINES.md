# RESPONSIVE UI GUIDELINES
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the responsive behavior, layout adaptation strategy, breakpoint system, and cross-device usability rules for the frontend system.

It establishes:
- responsive layout architecture
- breakpoint definitions
- adaptive dashboard behavior
- mobile/tablet/desktop UX rules
- chart responsiveness strategy
- usability constraints across devices

This document ensures the platform works consistently across all screen sizes.

---

# 2. PRIMARY OBJECTIVE

The responsive system exists to:
- ensure dashboard usability on all devices
- preserve analytical clarity across screen sizes
- maintain evaluator experience consistency
- adapt complex visualizations gracefully
- avoid information loss on smaller screens

The system must remain **analysis-first even on mobile**.

---

# 3. CORE RESPONSIVE PHILOSOPHY

The system follows:

### 3.1 Progressive Disclosure
Show critical data first, details on demand.

### 3.2 No Feature Removal on Mobile
All features must remain accessible.

### 3.3 Layout Adaptation, Not Simplification
UI should rearrange, not remove.

### 3.4 Analytical Priority Preservation
Safety insights must never be hidden.

---

# 4. BREAKPOINT SYSTEM

The UI uses standard responsive breakpoints:

```text id="breakpoints01"
Mobile      : < 640px
Tablet      : 640px – 1024px
Desktop     : 1024px – 1440px
Large Screen: > 1440px
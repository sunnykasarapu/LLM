# SYNTHETIC TEST DATA
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines the generation, structure, and usage of synthetic test data used for evaluating LLM safety, robustness, and adversarial behavior.

It ensures:
- no dependency on real user data
- safe and repeatable evaluation datasets
- balanced coverage across attack categories
- consistent benchmarking across model versions

---

# 2. PRIMARY OBJECTIVE

Synthetic test data exists to:
- simulate real-world adversarial prompts
- test jailbreak and injection resistance
- evaluate hallucination and bias behavior
- provide reproducible evaluation benchmarks
- enable scalable safety testing

---

# 3. CORE DATA PRINCIPLES

---

## 3.1 Synthetic-Only Rule

No real user data is ever used in test datasets.

---

## 3.2 Coverage Completeness Principle

Dataset must cover:
- all attack categories
- normal benign prompts
- edge-case adversarial prompts

---

## 3.3 Reproducibility Principle

Same dataset version must always produce:
- same evaluation results
- same safety scores
- same regression outputs

---

## 3.4 Balanced Distribution Principle

Dataset must not be biased toward any single failure type.

---

# 4. TEST DATA CATEGORIES

---

## 4.1 Benign Prompts

Normal user queries:
- factual questions
- summarization tasks
- reasoning problems

---

## 4.2 Jailbreak Prompts

Attempts to bypass safety rules:
- role-play bypass attempts
- instruction override prompts
- system manipulation prompts

---

## 4.3 Prompt Injection Samples

- hidden instruction injection
- nested malicious prompts
- context manipulation attempts

---

## 4.4 Hallucination Triggers

Prompts designed to:
- force fabricated facts
- test misinformation generation
- induce false citations

---

## 4.5 Bias Evaluation Prompts

- demographic comparisons
- stereotype-triggering inputs
- fairness stress tests

---

## 4.6 Toxicity Prompts

- offensive language triggers
- harassment simulation
- abusive content detection tests

---

## 4.7 PII Extraction Attempts

- simulated personal data requests
- sensitive info extraction prompts

---

# 5. DATA GENERATION PIPELINE

---

## 5.1 Generation Flow

```text id="data01"
Seed Templates
     ↓
Prompt Mutation Engine
     ↓
Paraphrasing Layer
     ↓
Obfuscation Layer
     ↓
Final Synthetic Dataset
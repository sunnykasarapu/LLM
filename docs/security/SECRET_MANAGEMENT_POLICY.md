# SECRET MANAGEMENT POLICY
## LLM Red-Teaming & Safety Evaluation Framework

---

# 1. DOCUMENT PURPOSE

This document defines how sensitive credentials such as API keys, database credentials, and service tokens are securely managed across development, testing, and production environments.

It ensures:
- no secret leakage into codebase
- secure handling of API credentials
- environment-safe configuration management
- controlled access to sensitive values
- production-grade secret isolation

---

# 2. PRIMARY OBJECTIVE

Secret management exists to:
- protect external API keys (Groq, HuggingFace)
- secure database credentials
- prevent accidental exposure in logs or UI
- enforce environment-based configuration
- support secure CI/CD pipelines

---

# 3. CORE SECURITY PRINCIPLES

The system follows:

### 3.1 Never Hardcode Secrets
No secret must exist inside source code.

### 3.2 Environment Isolation
Different environments must use separate credentials.

### 3.3 Least Exposure Principle
Only services that require a secret can access it.

### 3.4 No Frontend Secrets Rule
Frontend must never contain sensitive credentials.

---

# 4. TYPES OF SECRETS

---

## 4.1 External API Keys

- GROQ_API_KEY
- HF_API_KEY

Used for:
- LLM inference
- model evaluation requests

---

## 4.2 Database Credentials

- POSTGRES_USER
- POSTGRES_PASSWORD
- DATABASE_URL

Used for:
- evaluation storage
- audit logs
- regression tracking

---

## 4.3 Service Tokens

- Redis credentials (if secured)
- monitoring access tokens (Grafana/Prometheus optional auth)

---

# 5. SECRET STORAGE STRATEGY

---

## 5.1 Local Development

Secrets stored in:
```text id="secstore01"
.env file
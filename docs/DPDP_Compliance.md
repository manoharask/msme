# DPDP Act 2023 Compliance — Udyam Mitra Platform

> **Scope note:** This document covers both features implemented in the current demonstration prototype and planned roadmap items required for full DPDP Act 2023 compliance in a production deployment. Items marked **[DEMO]** are live in the running application. Items marked **[ROADMAP]** are architectural commitments planned for production release.

---

## Data Protection Measures

### 1. Data Encryption

| Control | Status | Detail |
|---|---|---|
| In Transit — TLS | **[DEMO]** | Neo4j Aura cloud connection uses TLS 1.3; OpenAI API calls use HTTPS |
| Temporary file cleanup | **[DEMO]** | Voice/PDF uploads written to OS temp location only for processing compatibility, then deleted in a `finally` cleanup block — no intentional retention |
| At Rest — AES-256 | **[ROADMAP]** | Neo4j Aura Enterprise provides encryption at rest; to be enabled in production deployment |

---

### 2. Access Control

**[DEMO]** — The current prototype operates without authentication (single-user demo mode).

**[ROADMAP]** — Production deployment will implement Role-Based Access Control (RBAC):

| Role | Access Level |
|---|---|
| Admin | Full access to all MSE data, SNP management, category management |
| MSE User | Access only to own registered MSE data |
| SNP User | View matched MSE contact information only |

Implementation: OAuth 2.0 via Streamlit-Authenticator or integration with MeitY's API Setu identity layer.

---

### 3. Data Minimization

| Practice | Status | Detail |
|---|---|---|
| Temporary upload handling | **[DEMO]** | Voice/PDF uploads processed in memory and deleted immediately after use |
| PII collection scope | **[DEMO]** | Only business-essential fields collected (name, city, products, URN, contact) |
| Optional fields | **[DEMO]** | Social category, incorporation date are optional in the onboarding form |

---

### 4. Consent Management

**[DEMO]** — Temporary file processing happens with implicit consent during the upload action.

**[ROADMAP]** — Production will require:
- Explicit checkbox before voice/document upload: *"I consent to processing this data for MSE registration"*
- Terms of service acceptance on first login
- Opt-in toggle for SNP matching notifications

---

### 5. User Rights (DPDP Compliance)

**[ROADMAP]** — The following data subject rights will be enabled in the production API layer:

| Right | Implementation Plan |
|---|---|
| Right to Access | `GET /api/mse/{urn}/data` — returns all stored data for an MSE |
| Right to Correction | Edit profile via Manage MSE page (UI exists; API endpoint planned) |
| Right to Deletion | Soft delete with 30-day grace period before permanent erasure |
| Data Portability | Export as JSON / CSV from the MSE detail view |

**[DEMO]** — MSE data can currently be updated by re-submitting with the same Udyam ID (MERGE semantics in Neo4j).

---

### 6. Audit Logging

**[ROADMAP]** — All sensitive operations will be logged in production:

```python
# Planned log structure
log_entry = {
    "timestamp": "2026-02-19T10:30:00Z",
    "user_id": "MSE_12345",
    "action": "VIEW_MSE_DATA",   # CREATE | UPDATE | DELETE | VIEW | EXPORT
    "resource_id": "MSE001",
    "ip_address": "103.x.x.x",
    "status": "SUCCESS"
}
```

Logs will be stored in a separate append-only collection with 7-year retention (statutory compliance requirement).

---

### 7. Data Retention Policy

**[ROADMAP]** — Production retention schedule:

| Data Type | Retention Period |
|---|---|
| MSE business data | 2 years post-registration (renewable) |
| Transaction logs | 90 days |
| Audit logs | 7 years (statutory requirement) |
| Deleted records | Permanently erased after 30-day grace period |

**[DEMO]** — The prototype retains all data until explicitly deleted via the Manage SNPs / Manage Categories UI, or via `python utils/reset_graph.py`.

---

### 8. Security Measures

| Measure | Status | Detail |
|---|---|---|
| Input validation | **[DEMO]** | Form fields validated before Neo4j write; Cypher uses parameterised MERGE |
| Temp file deletion | **[DEMO]** | `finally` blocks ensure temp files are always removed after OCR/voice processing |
| Cypher injection mitigation | **[DEMO — partial]** | GraphRAG pipeline generates Cypher via LLM; production would add a query allowlist / read-only Neo4j role |
| Rate limiting | **[ROADMAP]** | 100 requests/min per IP via API gateway (NGINX / Azure APIM) |
| Session management | **[ROADMAP]** | 30-minute session timeout with secure cookie handling |
| Password policy | **[ROADMAP]** | Min 8 chars, complexity required — applicable once RBAC is enabled |
| Network isolation | **[ROADMAP]** | Neo4j and OpenAI keys accessed via environment variables; production uses Azure Key Vault / AWS Secrets Manager |

# DPDP Act 2023 Compliance - MSME TEAM Platform

## Data Protection Measures

### 1. Data Encryption
- **At Rest:** AES-256 encryption for Neo4j database
- **In Transit:** TLS 1.3 for all API communications
- **Audio Files:** Deleted immediately after transcription (zero retention)

### 2. Access Control
- **RBAC Implementation:**
  - Admin: Full access to all MSE data
  - MSE User: Access only to own data
  - SNP User: View matched MSE contact info only
  
### 3. Data Minimization
- Voice audio: Not stored (processed in-memory)
- PII collection: Only business-essential fields
- Optional fields: Social category, incorporation date

### 4. Consent Management
- Explicit checkbox before voice upload
- Terms of service acceptance required
- Opt-in for SNP matching notifications

### 5. User Rights (DPDP Compliance)
- **Right to Access:** API endpoint /api/mse/{urn}/data
- **Right to Deletion:** Soft delete with 30-day grace period
- **Right to Correction:** Edit profile anytime
- **Data Portability:** Export as JSON/CSV

### 6. Audit Logging
```python
# All sensitive operations logged
log_entries = {
    "timestamp": "2026-02-19T10:30:00Z",
    "user_id": "MSE_12345",
    "action": "VIEW_MSE_DATA",
    "ip_address": "103.x.x.x",
    "status": "SUCCESS"
}
```

### 7. Data Retention Policy
- MSE business data: 2 years post-registration
- Transaction logs: 90 days
- Audit logs: 7 years (compliance requirement)
- Deleted data: Permanently erased after 30-day grace

### 8. Security Measures
- Input validation against SQL/Cypher injection
- Rate limiting: 100 requests/min per IP
- Session timeout: 30 minutes
- Password policy: Min 8 chars, complexity required
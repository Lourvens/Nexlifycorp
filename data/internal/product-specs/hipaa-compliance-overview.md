# HIPAA Compliance Overview

**Effective Date:** May 2026
**Next Review:** Q3 2026
**Classification:** INTERNAL — LEVEL 2 CONFIDENTIAL

---

## Overview

The Health Insurance Portability and Accountability Act (HIPAA) establishes national standards for protecting sensitive patient health information (PHI). Nexlify Corp provides HIPAA-compliant infrastructure for healthcare organizations processing PHI on the platform.

*Approved by: David Martinez, CISO*

---

## 1. HIPAA Readiness Status

| Capability | Status | Notes |
|-----------|--------|-------|
| Business Associate Agreement (BAA) | **Available** | Requires Enterprise plan |
| PHI Encryption | **Implemented** | AES-256 at rest, TLS 1.3 in transit |
| Audit Logging | **Implemented** | Comprehensive logging via Sentinel |
| Access Controls | **Implemented** | RBAC, SSO, MFA |
| Incident Response | **Available** | 24/7 security team |

---

## 2. Business Associate Agreement (BAA)

### 2.1 BAA Availability

A Business Associate Agreement (BAA) is available for customers on the **Enterprise** pricing tier. The BAA defines the responsibilities of Nexlify Corp as a business associate and establishes HIPAA compliance requirements.

### 2.2 Eligibility Requirements

To execute a BAA with Nexlify Corp:

| Requirement | Description |
|------------|-------------|
| Enterprise Plan | Customer must be on Enterprise tier |
| PHI Usage Agreement | Customer must agree to PHI handling terms |
| Security Assessment | Completion of security questionnaire |
| Active Contract | Valid subscription agreement |

### 2.3 Current BAA Negotiations

| Customer | Status | Notes |
|----------|--------|-------|
| HealthTech Inc | In negotiation | BAA under legal review |
| (Additional customers as applicable) | | |

---

## 3. Technical Safeguards

### 3.1 Encryption

| Data State | Encryption Standard | Implementation |
|-----------|--------------------|----------------|
| At Rest | AES-256 | All storage systems, databases |
| In Transit | TLS 1.3 | All API communications, mandatory |

**Implementation Notes:**
- Encryption keys managed via Platform key management
- Key rotation scheduled every 90 days
- Customer-managed keys available on Enterprise plan

### 3.2 Access Controls

| Control | Implementation |
|---------|---------------|
| Authentication | API keys + optional SSO via Sentinel |
| Authorization | Role-based access control (RBAC) |
| Session Management | 1-hour timeout, automatic logout |
| Multi-factor Authentication | Available via Sentinel add-on |

**Roles:**
- **Admin:** Full platform access
- **Engineer:** Inference access, no billing
- **Viewer:** Read-only access
- **External:** Limited to specific resources (Enterprise only)

### 3.3 Audit Logging

Comprehensive audit logging tracks:
- User authentication events
- API access patterns (enhancement via Sentinel)
- Data access and modifications
- Configuration changes
- Administrative actions

**Log Retention:** 6 years (HIPAA requirement)

---

## 4. Administrative Safeguards

### 4.1 Security Team

| Role | Contact |
|------|---------|
| CISO | David Martinez |
| HIPAA Compliance Officer | (Assigned per customer) |
| Incident Response | security@nexlifycorp.com |

### 4.2 Policies

| Policy | Status |
|--------|--------|
| Security Awareness Training | Implemented |
| Incident Response Plan | Implemented |
| Risk Assessment | Annual review |
| Business Continuity Plan | Implemented |

### 4.3 Employee Training

All Nexlify Corp employees with PHI access complete:
- HIPAA privacy training (annual)
- Security awareness training (quarterly)
- Incident reporting procedures

---

## 5. Physical Safeguards

### 5.1 Data Center Security

Nexlify Corp infrastructure is hosted in:
- SSAE 18 SOC 2 compliant data centers
- 24/7 physical security
- Biometric access controls
- CCTV surveillance
- Redundant power and cooling

### 5.2 Data Disposal

| Media Type | Disposal Method |
|-----------|-----------------|
| SSDs | Cryptographic erasure |
| HDDs | Physical destruction + cryptographic erasure |
| Tape | Degaussing + physical destruction |

---

## 6. Breach Notification

In the event of a HIPAA breach:

### 6.1 Notification Timeline

- **Initial Assessment:** Within 24 hours of discovery
- **Regulatory Notification:** Within 60 days (HHS)
- **Media Notification:** Within 60 days (if >500 affected)
- **Individual Notification:** Without unreasonable delay

### 6.2 Customer Notification

Nexlify Corp will notify affected customers within 48 hours of confirmed breach.

---

## 7. Compliance Roadmap

| Initiative | Target | Status |
|------------|--------|--------|
| HIPAA BAA availability | Available | **GA** |
| Sentinel integration | Q3 2026 | In Progress |
| Enhanced audit logging | Q3 2026 | In Progress |
| SOC 2 Type II audit | Q3 2026 | In Progress |
| FedRAMP Moderate | Q4 2026 | Planning |

---

## 8. Customer Responsibilities

Healthcare customers using Nexlify Corp for PHI processing are responsible for:

1. **Data Classification:** Properly labeling PHI within their applications
2. **Access Control:** Ensuring appropriate user access within their organization
3. **Encryption Keys:** Managing customer-managed keys (if using that feature)
4. **Audit Logging:** Enabling and reviewing Sentinel audit logs
5. **Breach Notification:** Reporting any suspected breaches to Nexlify Corp

---

## 9. Getting Started

### For New Customers

1. Contact your account manager to discuss HIPAA requirements
2. Complete the security assessment questionnaire
3. Execute the BAA during contract negotiation
4. Implement appropriate access controls in your application

### For Existing Customers

1. Contact support@nexlifycorp.com to initiate BAA process
2. Upgrade to Enterprise tier if not already on that plan
3. Review and update access controls
4. Enable Sentinel for enhanced audit logging

---

## 10. Resources

| Resource | Link |
|----------|------|
| BAA Request Form | (Contact your account manager) |
| Security Questionnaire | (Contact your account manager) |
| Compliance Documentation | docs.nexlifycorp.com/compliance |
| Incident Reporting | security@nexlifycorp.com |
| Support | support.nexlifycorp.com |

---

## Contact

| Role | Name | Responsibility |
|------|------|----------------|
| CEO | Michael Richardson | Overall accountability |
| CFO | Rebecca Chang | Financial compliance |
| CTO | Dr. Amanda Foster | Technical implementation |
| CISO | David Martinez | Security and compliance |

---

*Document Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
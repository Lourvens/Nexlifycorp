# SLA Definitions — Service Level Agreements

**Effective Date:** May 2026
**Document Version:** 2.0
**Classification:** INTERNAL — LEVEL 2 CONFIDENTIAL

---

## Overview

This document defines Service Level Agreements (SLAs) for the Nexlify Corp Platform across all pricing tiers. SLAs define the committed level of service, performance metrics, and remedies for non-compliance.

*Approved by: Rebecca Chang, CFO and Dr. Amanda Foster, CTO*

---

## 1. SLA Overview

### 1.1 Pricing Tier SLAs

| Tier | Monthly Price | Uptime SLA | Latency (P99) | Error Rate |
|------|--------------|------------|---------------|------------|
| Free | $0 | 99.0% | < 500ms | < 1% |
| Starter | $99 | 99.5% | < 300ms | < 0.5% |
| Platform | $499 | 99.9% | < 200ms | < 0.1% |
| Pro | $999 | 99.95% | < 150ms | < 0.05% |
| Enterprise | Custom | 99.99% | < 100ms | < 0.01% |

---

## 2. Uptime SLA Definition

### 2.1 Calculation Methodology

**Uptime Percentage** = (Total Minutes in Month - Downtime Minutes) / Total Minutes in Month × 100

**Downtime Definition:**
- Downtime begins when an incident is declared
- Downtime ends when service is restored
- Excludes scheduled maintenance (with 48h advance notice)
- Excludes force majeure events

### 2.2 Maximum Allowable Downtime by Tier

| Tier | Monthly Minutes | 99.0% | 99.5% | 99.9% | 99.95% | 99.99% |
|------|-----------------|-------|-------|-------|--------|--------|
| All | 43,200 | 432 min | 216 min | 43.8 min | 21.6 min | 4.3 min |

### 2.3 Tier-Specific Allowances

| Tier | Maximum Monthly Downtime |
|------|-------------------------|
| Free | 7 hours 12 minutes |
| Starter | 3 hours 36 minutes |
| Platform | 43.8 minutes |
| Pro | 21.6 minutes |
| Enterprise | 4.3 minutes |

---

## 3. Performance SLAs

### 3.1 Inference Latency

**Measurement Methodology:**
- Measured from request receipt to response start
- Excludes network transit time to/from customer
- Measured across all inference endpoints
- P99 calculated over rolling 30-day window

**Latency SLAs by Tier:**

| Tier | P50 | P95 | P99 |
|------|-----|-----|-----|
| Free | < 200ms | < 400ms | < 500ms |
| Starter | < 150ms | < 250ms | < 300ms |
| Platform | < 100ms | < 150ms | < 200ms |
| Pro | < 80ms | < 120ms | < 150ms |
| Enterprise | < 50ms | < 80ms | < 100ms |

### 3.2 API Availability

**API Availability Definition:**
- Successful requests (2xx/3xx responses) divided by total requests
- Measured across all API endpoints
- Excludes customer-side network issues

**Availability Calculation:**
```
API Availability % = (Successful Requests / Total Requests) × 100
```

---

## 4. Error Rate SLAs

### 4.1 Error Rate Definition

**Error Rate** = (Failed Requests / Total Requests) × 100

**Failed Request Classification:**
- HTTP 4xx errors (excluding 429 rate limit)
- HTTP 5xx errors
- Request timeouts
- Internal errors

### 4.2 Error Rate Targets

| Tier | Maximum Error Rate |
|------|-------------------|
| Free | 1.0% |
| Starter | 0.5% |
| Platform | 0.1% |
| Pro | 0.05% |
| Enterprise | 0.01% |

---

## 5. SLA Credit Remedies

### 5.1 Credit Calculation

When Nexlify Corp fails to meet SLA commitments, customers are eligible for service credits:

| SLA Violation | Credit Formula |
|---------------|----------------|
| Uptime below commitment | Monthly fee × credit percentage |
| Latency above P99 commitment | Monthly fee × 10% |
| Error rate above commitment | Monthly fee × 10% |

### 5.2 Credit Schedule

| Downtime (Platform Tier) | Credit |
|-------------------------|--------|
| < 43.8 minutes | None |
| 43.8 min — 4.38 hours | 10% of monthly fee |
| 4.38 — 8.76 hours | 25% of monthly fee |
| > 8.76 hours | 50% of monthly fee |

### 5.3 Credit Limitations

- Maximum credit: 50% of monthly fee
- Credits apply to future billing, not refunds
- Credits must be requested within 30 days of incident
- Enterprise tier has custom SLA with negotiated credits

---

## 6. Maintenance Windows

### 6.1 Scheduled Maintenance

| Type | Notice Required | Impact |
|------|-----------------|--------|
| Planned | 48 hours | May cause brief downtime |
| Emergency | As much as possible | May cause downtime |

**Preferred Maintenance Windows:**
- Americas: Sunday 2:00 AM — 6:00 AM UTC
- Europe: Sunday 1:00 AM — 5:00 AM UTC
- Asia-Pacific: Saturday 10:00 PM — 2:00 AM UTC

### 6.2 Exclusions from SLA Calculation

The following are excluded from SLA calculations:
- Scheduled maintenance (with advance notice)
- Force majeure events
- Customer-induced issues
- Third-party service failures outside Nexlify Corp control

---

## 7. Incident Response

### 7.1 Severity Classification

| Severity | Definition | Response Time |
|----------|------------|--------------|
| Critical | Platform unavailable | < 15 minutes |
| High | Major feature impaired | < 1 hour |
| Medium | Minor feature impaired | < 4 hours |
| Low | Cosmetic/minor issue | < 8 hours |

### 7.2 Response Times by Tier

| Tier | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| Free | — | — | — | — |
| Starter | — | < 4 hours | < 24 hours | < 72 hours |
| Platform | < 8 hours | < 2 hours | < 8 hours | < 48 hours |
| Pro | < 1 hour | < 1 hour | < 4 hours | < 24 hours |
| Enterprise | < 15 min | < 30 min | < 2 hours | < 8 hours |

---

## 8. Support Response SLAs

### 8.1 Support Channels

| Tier | Channels | Hours |
|------|----------|-------|
| Free | Community forum | Best effort |
| Starter | Email, Chat | Business hours |
| Platform | Email, Chat | Business hours |
| Pro | Email, Chat, Phone | 24/5 |
| Enterprise | Dedicated Slack, Phone | 24/7 |

### 8.2 Response Time SLAs

| Priority | Platform | Pro | Enterprise |
|----------|----------|-----|------------|
| Critical | < 8 hours | < 1 hour | < 15 minutes |
| High | < 24 hours | < 4 hours | < 30 minutes |
| Medium | < 48 hours | < 24 hours | < 2 hours |
| Low | < 5 days | < 48 hours | < 8 hours |

---

## 9. Enterprise SLA Customization

### 9.1 Custom SLA Options

Enterprise customers may negotiate:
- Custom uptime commitments (>99.99%)
- Dedicated support engineers
- On-site support availability
- Custom latency guarantees
- Disaster recovery SLAs

### 9.2 Multi-Region Failover — Project Meridian

For Enterprise customers requiring multi-region failover:
- **Product:** Nexlify Globe (codename: Meridian)
- **Target:** Q4 2026
- **RTO:** < 30 seconds
- **RPO:** < 5 minutes

---

## 10. SLA Review and Modification

### 10.1 Review Cycle

- SLA terms reviewed annually
- Customers notified 30 days before changes
- New pricing tiers may introduce new SLAs

### 10.2 Modification Process

1. Proposed changes documented
2. Customer notification (30 days minimum)
3. Customer acceptance required
4. Updated SLA takes effect at renewal

---

## 11. Contact Information

| Role | Name | Responsibility |
|------|------|----------------|
| CFO | Rebecca Chang | Financial SLA matters |
| CTO | Dr. Amanda Foster | Technical SLA matters |
| VP Security | Jennifer Wu | Security SLA matters |

---

*Document Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
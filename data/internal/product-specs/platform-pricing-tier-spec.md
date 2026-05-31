# Platform Pricing Tier — Specification

**Effective Date:** May 2026
**Classification:** INTERNAL — LEVEL 2 CONFIDENTIAL

---

## Overview

The Platform pricing tier occupies the mid-market position between Starter and Pro, delivering enhanced capabilities for growing teams requiring production-grade infrastructure without enterprise-level commitment.

*Approved by: Rebecca Chang, CFO and Dr. Sarah Kim, CPO*

---

## 1. Tier Positioning

### Pricing Tier Comparison

| Tier | Monthly Price | GPU Hours | API Calls | Target Customer |
|------|--------------|-----------|-----------|-----------------|
| Free | $0 | 10 | 1,000 | Evaluation |
| Starter | $99 | 100 | 10,000 | Individual developers |
| **Platform** | **$499** | **500** | **50,000** | **Growing teams** |
| Pro | $999 | 1,000 | 100,000 | Production workloads |
| Enterprise | Custom | Unlimited | Unlimited | Large enterprises |

### Platform Tier Value Proposition

- **5x** the resources of Starter tier
- **Enhanced** SLA (99.9% uptime)
- **Pulse Analytics** available ($79 add-on)
- **Sentinel** available ($199 add-on)
- Priority support during business hours

---

## 2. Platform Tier Specifications

### 2.1 Compute Resources

| Resource | Allowance |
|----------|-----------|
| GPU Hours | 500 hours/month |
| Concurrent Inference Requests | 50 |
| Model Deployment Slots | 10 |
| Storage | 100 GB |

**Overage Policy:**
- GPU Hours: $0.08/minute overage
- Storage: $0.10/GB/day overage

### 2.2 API Limits

| Limit Type | Value |
|------------|-------|
| API Calls | 50,000/month |
| Rate Limit | 1,000 requests/minute |
| Burst Limit | 150 requests |

### 2.3 Supported Models

Platform tier includes access to:
- All NEXL-X3 optimized models
- Claude 3 family models (Sonnet, Haiku)
- Custom model hosting (up to 3 models)
- Model fine-tuning (basic)

---

## 3. Platform Tier Features

### 3.1 Core Features (Included)

| Feature | Description |
|---------|-------------|
| Inference API | REST API for model inference |
| SDK Access | Full SDK v2.3 access |
| Monitoring Dashboard | Basic metrics (Pulse add-on for advanced) |
| Team Collaboration | Up to 10 team members |
| Project Support | Up to 5 projects |
| SSL/TLS | TLS 1.3 encryption |
| Uptime SLA | 99.9% |

### 3.2 Platform Add-ons

| Add-on | Monthly Cost | Included in Platform? |
|--------|--------------|----------------------|
| Pulse Analytics | $79 | Available (optional) |
| Sentinel Security | $199 | Available (optional) |

### 3.3 Support Level

| Support Feature | Platform Tier |
|----------------|---------------|
| Support Channel | Email + Chat (business hours) |
| Response Time | < 8 hours (business days) |
| Documentation | Full access |
| API Status Page | Yes |

---

## 4. SLA Specification

### Platform Tier SLA

| Metric | Value |
|--------|-------|
| Monthly Uptime | 99.9% |
| Maximum Monthly Downtime | 43.8 minutes |
| Latency (P99) | < 200ms for inference |
| Error Rate | < 0.1% |

**SLA Credits:**

| Downtime (Monthly) | Credit |
|--------------------|--------|
| < 43.8 minutes | None |
| 43.8 min — 4.38 hours | 10% of monthly fee |
| 4.38 — 8.76 hours | 25% of monthly fee |
| > 8.76 hours | 50% of monthly fee |

---

## 5. Use Cases

### Primary Use Cases for Platform Tier

1. **Early-stage Production:** Teams graduating from Starter tier
2. **SMB Infrastructure:** Small to medium businesses with moderate inference needs
3. **Development Environments:** Staging and testing for larger organizations
4. **Pilot Programs:** Enterprise teams piloting before full deployment

### Not Recommended For

- Mission-critical production (Pro or Enterprise recommended)
- High-volume batch processing (Pro recommended)
- Compliance-sensitive workloads (Enterprise required for HIPAA BAA)

---

## 6. Competitive Differentiation

| Feature | Platform vs. Starter | Platform vs. Pro |
|---------|---------------------|-----------------|
| GPU Hours | 5x more | Half |
| API Calls | 5x more | Half |
| SLA | 99.9% vs 99.5% | 99.9% vs 99.95% |
| Concurrent Requests | 50 vs 10 | 50 vs 100 |
| Pulse Analytics | Optional vs excluded | Optional vs included |

---

## 7. Migration Paths

### Upgrade from Starter to Platform

**Process:**
1. Contact sales or upgrade via dashboard
2. Existing API keys remain valid
3. Rate limits increase immediately
4. GPU hours prorated for remainder of billing cycle

**Benefits:**
- Immediate access to 5x resources
- 99.9% SLA vs 99.5%
- Access to add-ons

### Upgrade from Platform to Pro

**Process:**
1. Contact sales for Pro tier
2. Custom pricing may apply
3. 1000 GPU hours and 100,000 API calls
4. 99.95% SLA

---

## 8. Implementation Notes

### Technical Requirements

| Requirement | Notes |
|-------------|-------|
| API Version | v2.3 or higher |
| SDK Compatibility | Full support |
| Authentication | API keys, optional SSO via Sentinel |

### Rate Limiting Behavior

When rate limit exceeded:
- HTTP 429 response
- Retry-After header with seconds
- Exponential backoff recommended

---

## 9. Financial Summary

### Monthly Cost Breakdown

| Component | Cost |
|-----------|------|
| Platform Base | $499 |
| Pulse Analytics (optional) | +$79 |
| Sentinel Security (optional) | +$199 |
| **Total with Add-ons** | **$499 — $777** |

### Annual Pricing

| Plan | Monthly | Annual | Savings |
|------|---------|--------|---------|
| Platform | $499 | $4,990 | 2 months free |
| Platform + Pulse | $578 | $5,780 | 2 months free |
| Platform + Sentinel | $698 | $6,980 | 2 months free |

---

## 10. Approval and Ownership

| Role | Name | Responsibility |
|------|------|----------------|
| CFO | Rebecca Chang | Financial approval |
| CPO | Dr. Sarah Kim | Product direction |
| VP Sales | James Rodriguez | Customer pricing |
| VP Engineering | Robert Chen | Technical delivery |

---

*Document Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
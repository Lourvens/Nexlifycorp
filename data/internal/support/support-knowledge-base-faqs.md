# Nexlify Corp — Support Knowledge Base FAQ

**Document Version:** 2.1
**Effective Date:** January 15, 2026
**Owner:** Customer Success Team
**Classification:** INTERNAL — LEVEL 2 CONFIDENTIAL

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Oct 12, 2025 | Maria Santos, Support Manager | Initial release |
| 1.5 | Nov 20, 2025 | Maria Santos | Added post-breach FAQ items |
| 2.0 | Dec 8, 2025 | Maria Santos | Added Pulse/Sentinel FAQs |
| 2.1 | Jan 15, 2026 | Maria Santos | Q1 2026 update |

---

## Introduction

This document provides Nexlify Corp's support team with a comprehensive FAQ knowledge base for handling common customer inquiries. Use these Q&A pairs as reference when responding to tickets. Always verify current system status and account details before providing guidance.

**Tools Referenced:** Salesforce (ticket management), PagerDuty (on-call escalation), Slack (#support tier-1, #support tier-2, #support tier-3)

---

## Section 1: Account & Billing FAQs

### FAQ 1.1: How do I upgrade my account tier?

**Question:** "I want to upgrade from Starter to Platform tier. How do I do this?"

**Answer:**

You can upgrade your account tier through the following methods:

1. **Self-service via Dashboard:** Navigate to Settings > Subscription > Change Plan and select your desired tier
2. **Contact Sales:** For Platform-to-Pro or Enterprise upgrades, our sales team can create a custom quote
3. **API Key Migration:** Upgrading does not invalidate existing API keys. New rate limits apply immediately upon upgrade

**Rate Limit Changes Upon Upgrade:**

| Upgrade Path | Old RPM | New RPM |
|-------------|---------|---------|
| Free → Starter | 60 | 300 |
| Starter → Platform | 300 | 1,000 |
| Platform → Pro | 1,000 | 3,000 |
| Pro → Enterprise | 3,000 | 10,000 |

**Important Notes:**
- Upgrades take effect immediately
- GPU hours are prorated for the billing cycle
- Annual commitments include 2 months free

**Verification Steps:**
1. Confirm current tier in Salesforce account record
2. Verify rate limit headers reflect new limits after upgrade: `X-RateLimit-Limit`
3. Check GPU hour allocation in dashboard

---

### FAQ 1.2: Why was I charged overage fees?

**Question:** "I received a charge on my invoice that I don't understand. Can you explain the GPU hour overage?"

**Answer:**

GPU hour overages occur when usage exceeds the monthly tier allocation. Here's how it works:

**Platform Tier Example:**
- Included: 500 GPU hours/month
- Overage rate: $0.08/minute (not hour)
- Overage threshold: After 500 hours are consumed

**Calculation Example:**
If you used 510 GPU hours (10 hours over):
- First 500 hours: Covered by base $499/month
- 10 additional hours = 600 minutes × $0.08 = $48 overage charge

**How to Monitor Usage:**
1. Check Pulse Analytics dashboard for real-time GPU hour consumption
2. Set up usage alerts in Settings > Notifications > Usage Thresholds
3. Review endpoint `/api/v2/usage` for detailed breakdown

**To Prevent Overage:**
- Enable automatic notifications at 75% and 90% usage
- Consider upgrading to Pro tier for 1,000 GPU hours
- Implement batch processing to optimize GPU utilization

---

### FAQ 1.3: How do I request a refund?

**Question:** "I believe I was incorrectly charged. How can I request a refund?"

**Answer:**

Refund requests are processed through Salesforce. Here's the process:

1. **Log the ticket** in Salesforce with subject "Billing Inquiry - Refund Request"
2. **Required information:**
   - Invoice number
   - Date of charge
   - Dollar amount
   - Reason for refund request
3. **Escalation path:**
   - Tier 1 reviews and approves refunds under $100
   - Tier 2 approves refunds $100-$500
   - Finance team approves refunds over $500

**Refund Policy Notes:**
- Credits from SLA violations are applied to future billing, not refunded
- Refunds must be requested within 30 days of charge
- Annual plan refunds are prorated based on unused months

**Recent Known Issue:**
Following the November 2025 cybersecurity incident, affected Enterprise customers may have received duplicate billing entries. If you received a November 2025 invoice with unusual charges, please reference ticket case #INC-2025-NF-042 in your request.

---

## Section 2: Technical Integration FAQs

### FAQ 2.1: How do I migrate from v1 to v2 API?

**Question:** "We're still using v1 API endpoints. What is the migration path to v2?"

**Answer:**

The v2 API migration is required for all customers. v1 endpoints will be deprecated on **June 1, 2026**.

**Key Changes in v2:**

| Aspect | v1 | v2 |
|--------|----|----|
| Base URL | `https://api.nexlify.com/v1` | `https://api.nexlify.com/v2` |
| Authentication | API Key only | API Key + OAuth 2.0 |
| Rate Limit Header | `X-API-Limit` | `X-RateLimit-Limit` |
| Error Format | `{ "error": "message" }` | `{ "error": { "code": "ERROR_CODE", "message": "..." } }` |

**Migration Steps:**
1. Update base URL from `/v1/` to `/v2/`
2. Replace error handling logic (v2 uses structured error objects)
3. Implement OAuth 2.0 for enhanced security (required for Enterprise)
4. Test rate limit headers match expected values
5. Update any deprecated endpoint paths

**Breaking Changes:**
- `/v1/inference` → `/v2/inference` (same functionality)
- `/v1/training` → `/v2/training` (same functionality)
- `/v1/models` → `/v2/models` (response format changed)

**SDK Migration:**
```python
# Old v1
from nexlify import Client
client = Client(api_key="nx_live_xxx")

# New v2
from nexlify.v2 import Client
client = Client(api_key="nx_live_xxx", oauth_token="oauth_xxx")
```

**Support:** For complex migrations, request a technical migration call with our solutions engineering team via Salesforce case type "Technical Migration."

---

### FAQ 2.2: How do I handle 429 rate limit errors?

**Question:** "I'm getting 429 errors even though I think I'm within my limit. What's happening?"

**Answer:**

A 429 error indicates you've exceeded your rate limit. However, there are several possible causes:

**Possible Causes:**

1. **Plan limit exceeded** - Check `X-RateLimit-Limit` header for your tier's limit
2. **Endpoint-specific limits** - `/api/v2/inference` has 100 RPM limit even on Enterprise
3. **Burst limit exceeded** - Platform tier has 150 request burst limit
4. **Multiple API keys** - Rate limits are per-key, not per-account

**Diagnostic Steps:**
1. Check response headers:
   ```
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 0
   X-RateLimit-Reset: 1704067260
   Retry-After: 60
   ```

2. If `X-RateLimit-Remaining: 0` but you're under plan limit, check endpoint limits

3. Verify you're not using multiple API keys that each hit limits

**Best Practices for Rate Limit Handling:**
```python
import time
import requests

def call_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, headers={"Authorization": "Bearer nx_live_xxx"})
        if response.status_code == 429:
            wait_seconds = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds * (2 ** attempt))  # Exponential backoff
        else:
            return response
    raise Exception("Max retries exceeded")
```

**Increasing Limits:**
- Temporary burst: Implement exponential backoff
- Permanent increase: Upgrade tier or contact Enterprise sales for custom limits

---

### FAQ 2.3: How do I set up webhooks?

**Question:** "I want to receive real-time notifications for inference job completions. How do I configure webhooks?"

**Answer:**

Webhooks allow real-time event delivery without polling. Configuration steps:

**Webhook Setup:**
1. Navigate to Dashboard > Settings > Webhooks
2. Add endpoint URL (must be HTTPS)
3. Select events to subscribe to
4. Note your webhook signing secret

**Available Webhook Events:**

| Event | Description |
|-------|-------------|
| `inference.job.completed` | Inference job finished |
| `inference.job.failed` | Inference job failed |
| `training.job.completed` | Training job finished |
| `training.job.failed` | Training job failed |
| `model.deployed` | Model deployment complete |
| `model.undeployed` | Model removed from production |
| `alert.threshold_exceeded` | Usage threshold reached |
| `security.anomaly_detected` | Sentinel detected anomaly (Sentinel customers only) |

**Webhook Payload Example:**
```json
{
  "event": "inference.job.completed",
  "timestamp": "2026-01-15T14:32:00Z",
  "data": {
    "job_id": "job_abc123",
    "model": "nexl-x3-standard",
    "duration_ms": 245,
    "output_tokens": 512
  }
}
```

**Security Verification:**
Verify webhook signatures using the `X-Nexlify-Signature` header:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

**Webhook Rate Limits:**

| Tier | Webhooks | Events/minute |
|------|---------|---------------|
| Free/Starter | 1 endpoint | 60 |
| Platform | 3 endpoints | 300 |
| Pro | 5 endpoints | 1,000 |
| Enterprise | 10 endpoints | 5,000 |

---

### FAQ 2.4: Why is my inference latency higher than the SLA?

**Question:** "I'm seeing P99 latency of 350ms on Platform tier, but the SLA says <200ms. Why is this?"

**Answer:**

Several factors can cause latency above SLA thresholds:

**1. Cold Start Latency**
- First request to a model after deployment has higher latency (model loading)
- Solution: Enable "Always On" mode for critical models (Pro+ tier)

**2. Request Queueing**
- If you're exceeding concurrent request limits, requests queue
- Platform tier: 50 concurrent inference requests
- Check: `X-Queue-Depth` header in response

**3. Burst Traffic**
- Platform tier burst limit: 150 requests
- Excess requests queue behind burst
- Solution: Implement client-side rate limiting

**4. Network Transit**
- SLA latency is measured server-side (request receipt to response start)
- Network transit to/from customer is excluded
- Solution: Consider edge deployment for latency-sensitive workloads

**5. Payload Size**
- Large input/output payloads increase processing time
- Solution: Optimize prompt length, consider streaming for large outputs

**Diagnostic Approach:**
1. Check if latency is consistent or intermittent
2. Monitor `X-Processing-Time` header for server-side processing time
3. Review Pulse Analytics for latency breakdown by endpoint
4. Confirm no queueing via `X-Queue-Depth`

**If Latency Violates SLA:**
- Document specific timestamps and request IDs
- Open Salesforce case with "SLA Inquiry" type
- Eligible for service credits per SLA terms

---

## Section 3: Security & Compliance FAQs

### FAQ 3.1: What happened in the November 2025 security incident?

**Question:** "I heard Nexlify had a security incident. Should I be concerned about my data?"

**Answer:**

We are committed to transparency with our customers. Here is what occurred:

**Incident Summary (November 2025):**
- Advanced persistent threat (APT) actor gained access to corporate network
- Access was achieved through a sophisticated phishing campaign
- Duration of access: Approximately 94 days before detection
- Containment: October 31, 2025

**What Was Affected:**
- Corporate systems (not customer-facing production infrastructure)
- Some internal corporate documents
- **Customer production data was NOT affected**
- Our production environment is isolated from corporate systems

**Actions Taken:**
- Immediate containment and threat termination
- Full password reset for all employees
- Enhanced security controls deployed
- FBI and CISA engagement
- Third-party security audit completed

**Customer Impact Assessment:**
- **No customer API keys were compromised**
- **No customer data was exfiltrated**
- Customer production systems remained secure throughout
- Additional Sentinel security monitoring available at no cost to affected customers

**For Sentinel Customers:**
Sentinel detected anomalous activity patterns during the incident window and provided alerts. If you received Sentinel alerts in October 2025, please review case #INC-2025-NF-042 in your security logs.

**Questions?** Contact your Customer Success Manager or open a Salesforce case referencing the incident ID.

---

### FAQ 3.2: How do I rotate API keys?

**Question:** "I want to rotate my API keys for security purposes. How do I do this?"

**Answer:**

API key rotation can be performed through the dashboard or API:

**Dashboard Method:**
1. Navigate to Settings > API Keys
2. Click "Generate New Key"
3. New key becomes active immediately
4. Update your applications with new key
5. Delete old key after verifying new key works

**API Method:**
```http
POST /api/v2/api-keys/rotate
Authorization: Bearer nx_live_old_key
```

**Important Rotation Notes:**
- Old key remains valid for 24 hours after rotation (grace period)
- Both keys work during transition window
- Rate limits are per-key, not transferred during rotation
- Active requests using old key complete normally

**When to Rotate:**
- Annually as best practice
- After any potential credential exposure
- When team member with key access leaves
- After security incidents (like the November 2025 event)

**Enterprise Customers:**
Consider implementing automatic key rotation via our API with your secrets manager. Contact Solutions Engineering for integration assistance.

---

### FAQ 3.3: Does Nexlify support HIPAA compliance?

**Question:** "We're a healthcare company and need HIPAA-compliant infrastructure. What does Nexlify offer?"

**Answer:**

Nexlify offers HIPAA-compliant infrastructure for Enterprise tier customers:

**HIPAA Compliance Options:**

| Component | Availability |
|-----------|--------------|
| BAA (Business Associate Agreement) | Enterprise tier only |
| PHI environment isolation | Enterprise tier only |
| Audit logging | Sentinel add-on required |
| Data encryption at rest | All tiers (AES-256) |
| Data encryption in transit | All tiers (TLS 1.3) |

**Enterprise HIPAA Setup:**
1. Contact Sales to upgrade to Enterprise tier
2. Request BAA agreement (typically 1-2 weeks for legal review)
3. Enable Sentinel for audit logging (required for HIPAA)
4. Configure dedicated PHI environment

**What's Covered Under BAA:**
- Inference processing of PHI
- Secure model deployment
- Audit trail via Sentinel
- Incident notification procedures

**What's NOT Covered:**
- Customer applications built on platform
- Data customer stores in our system outside of inference
- End-user devices accessing the platform

**Pricing:**
- Enterprise base + Sentinel add-on ($199/month) + BAA admin fee
- Contact Enterprise sales for custom quote

---

### FAQ 3.4: How does Sentinel detect anomalies?

**Question:** "I subscribed to Sentinel. What kinds of threats does it detect?"

**Answer:**

Sentinel provides comprehensive security monitoring for your Nexlify infrastructure:

**Sentinel Detection Capabilities:**

| Category | Detection |
|----------|----------|
| **Authentication Anomalies** | Unusual login locations, failed attempts, impossible travel |
| **API Abuse** | Abnormal request patterns, credential stuffing attempts |
| **Rate Limit Bypass** | Attempts to circumvent rate limiting |
| **Data Exfiltration** | Unusual data access or transfer patterns |
| **Model Attacks** | Prompt injection, adversarial inputs |
| **Insider Threats** | Privileged user anomalies |

**Alert Severity Levels:**

| Level | Description | Response Time |
|-------|-------------|---------------|
| Critical | Immediate threat, data exposure risk | < 15 min (Pro/Enterprise) |
| High | Likely threat, investigation required | < 1 hour |
| Medium | Possible threat, monitoring heightened | < 4 hours |
| Low | Informational, unlikely threat | < 24 hours |

**Sentinel Dashboard:**
- Real-time threat dashboard
- Historical alert analysis
- Automated response playbooks
- Integration with your SIEM via webhook

**November 2025 Incident Note:**
During the November 2025 security incident, Sentinel detected the anomalous service account activity that led to discovery of the breach. Sentinel's behavioral analysis would have detected the intrusion earlier if the compromised account had been in scope for Sentinel monitoring.

---

## Section 4: Product-Specific FAQs

### FAQ 4.1: What is the difference between NEXL-X3 and NEXL-E1?

**Question:** "I see both NEXL-X3 and NEXL-E1 in the documentation. When should I use each?"

**Answer:**

NEXL-X3 and NEXL-E1 serve different use cases:

| Feature | NEXL-X3 | NEXL-E1 |
|---------|---------|---------|
| **Primary Use** | Data center inference | Edge deployment |
| **Form Factor** | Server/rack mount | Compact edge device |
| **Connectivity** | Ethernet, fiber | WiFi, 5G, Ethernet |
| **Latency** | < 100ms P99 (Enterprise) | < 50ms P99 (local) |
| **Offline Mode** | No | Yes |
| **Power** | 500W TDP | 50W TDP |
| **Intended For** | Cloud inference at scale | On-premise/edge inference |

**NEXL-X3 Best For:**
- High-volume cloud inference
- Batch processing workloads
- When you need maximum throughput
- Standard API integration

**NEXL-E1 Best For:**
- IoT and edge computing scenarios
- Low-latency requirements (<50ms)
- Environments with limited connectivity
- Privacy-sensitive data (processing stays on-premise)

**Example Use Cases:**
- NEXL-X3: "Process 10,000 customer support tickets per hour for sentiment analysis"
- NEXL-E1: "Real-time quality inspection on manufacturing floor with no cloud connectivity"

**Migration Path:**
NEXL-E1 uses the same API as NEXL-X3 (v2). Models optimized for X3 may require light retraining for E1 deployment.

---

### FAQ 4.2: How do I deploy a model with Pulse Analytics?

**Question:** "I want to monitor my model's performance. How do I enable Pulse Analytics?"

**Answer:**

Pulse Analytics provides real-time and historical performance monitoring:

**Enabling Pulse Analytics:**
1. Subscribe to Pulse add-on ($79/month for Platform tier, included with Pro+)
2. Navigate to Dashboard > Pulse
3. Select your deployed model
4. Configure metrics and alerts

**Available Pulse Metrics:**

| Metric | Description |
|--------|-------------|
| Request Volume | Requests per minute/hour/day |
| Latency Distribution | P50, P95, P99 response times |
| Error Rate | Failed requests as percentage |
| GPU Utilization | Percent of GPU capacity used |
| Token Throughput | Input/output tokens per second |
| Cost per Request | Calculated inference cost |

**Setting Up Alerts:**
```python
# Pulse Alert Configuration
alert_config = {
    "metric": "latency_p99",
    "threshold": 250,  # ms
    "operator": "greater_than",
    "duration": "5m",  # sustained for 5 minutes
    "action": "email_and_webhook"
}
```

**Pulse Dashboard Sections:**
1. **Overview** - High-level metrics, trend lines
2. **Real-time** - Live request stream, current latency
3. **Historical** - Deep dive into past performance
4. **Cost Analysis** - Spend tracking and optimization
5. **Alerts** - Active and historical alerts

**Common Issues:**
- If Pulse shows "No Data," verify model is actively processing requests
- Alert notifications require webhook endpoint configured in Settings > Notifications

---

### FAQ 4.3: What is NEXL-SW and do I need it?

**Question:** "I see references to NEXL-SW in documentation. What is it and should I use it?"

**Answer:**

NEXL-SW (Nexlify Software Stack) is our proprietary software layer for optimized model execution:

**NEXL-SW Components:**

| Component | Function |
|-----------|----------|
| **NEXL-SW Runtime** | Optimized inference execution |
| **NEXL-SW SDK** | API wrapper and utilities |
| **NEXL-SW Manager** | Deployment and monitoring |
| **NEXL-SW Security** | Model protection, watermarking |

**When NEXL-SW is Required:**
- Deploying models on NEXL-E1 edge devices
- Using advanced model protection features
- Custom model optimization for latency-critical applications

**NEXL-SW Versions:**

| Version | Status | Key Features |
|---------|--------|--------------|
| 3.x | Current | Basic inference optimization |
| 4.0 | Beta | Advanced security features, watermarking |
| 4.0 (GA) | Q2 2026 | Full feature set |

**Installation:**
```bash
pip install nexlify-sw==3.2.1
```

**Migration to 4.0 (when available):**
- 4.0 is a major version with breaking changes
- Beta testing available Q1 2026
- GA release scheduled Q2 2026
- Migration guide will be provided 30 days before GA

**For Most Customers:**
- NEXL-SW is optional for cloud API users
- Required for NEXL-E1 deployment
- Provides 15-30% latency improvement when used

---

### FAQ 4.4: How do I report a suspected security vulnerability?

**Question:** "I think I found a security vulnerability in the Nexlify platform. How should I report it?"

**Answer:**

We take security seriously. Here's how to report vulnerabilities:

**Responsible Disclosure Process:**

1. **DO NOT** submit vulnerability details in public tickets
2. **Email:** security@nexlify.com (encrypted preferred with PGP)
3. **Salesforce:** Create case with type "Security - Confidential"
4. **Direct Contact:** Request CISO escalation if severity is Critical

**What to Include:**
- Description of vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested remediation (if any)

**Response Timeline:**

| Severity | Initial Response | Target Resolution |
|----------|------------------|-------------------|
| Critical | < 24 hours | 7 days |
| High | < 48 hours | 30 days |
| Medium | < 5 days | 90 days |
| Low | < 10 days | Next release |

**Bug Bounty Program:**
Nexlify participates in HackerOne bug bounty. Submit vulnerabilities there for potential bounty rewards:
- Critical: $10,000 - $50,000
- High: $2,500 - $10,000
- Medium: $500 - $2,500
- Low: $100 - $500

**For Urgent Vulnerabilities (Production Down):**
- Call our 24/7 security hotline: +1-888-NEXL-SEC (external customers)
- Enterprise customers: Use PagerDuty escalation path

---

## Section 5: SLA & Support Tier FAQs

### FAQ 5.1: How do I file an SLA credit request?

**Question:** "My service was down and I believe I'm eligible for SLA credits. How do I request them?"

**Answer:**

SLA credit requests must be filed within 30 days of the incident:

**Filing Process:**
1. **Verify Eligibility:** Check if downtime exceeded your tier's maximum allowable downtime

| Tier | Max Monthly Downtime | Credit Threshold |
|------|---------------------|------------------|
| Free | 7h 12m | None |
| Starter | 3h 36m | >3h 36m |
| Platform | 43.8 min | >43.8 min |
| Pro | 21.6 min | >21.6 min |
| Enterprise | 4.3 min | >4.3 min |

2. **Log Salesforce Case:** Type "SLA Credit Request"
3. **Required Information:**
   - Dates and times of outage (with timezone)
   - Duration of impact
   - Description of impact
   - Ticket/incident ID (if known)
   - Evidence (screenshots, logs showing impact)

4. **Credit Calculation:**

| Downtime (Platform Tier) | Credit |
|-------------------------|--------|
| 43.8 min — 4.38 hours | 10% of monthly fee |
| 4.38 — 8.76 hours | 25% of monthly fee |
| > 8.76 hours | 50% of monthly fee |

**Credit Limitations:**
- Maximum credit: 50% of monthly fee
- Credits apply to future billing, not refunds
- Credits are applied automatically for verified incidents

**Recent Incident Credit:**
For the November 2025 incident, affected customers received automatic credits. Verify your invoice for November/December 2025 for applied credits.

---

### FAQ 5.2: What are the support tiers and how do I escalate?

**Question:** "I have a critical issue. How do I escalate to Tier 3 support?"

**Answer:**

Support tier escalation is based on issue severity and your service tier:

**Support Channels by Tier:**

| Tier | Channels | Hours |
|------|----------|-------|
| Free | Community forum | Best effort |
| Starter | Email, Chat | Business hours |
| Platform | Email, Chat | Business hours |
| Pro | Email, Chat, Phone | 24/5 (PST business hours) |
| Enterprise | Dedicated Slack, Phone | 24/7 |

**Escalation Process:**

1. **For Platform/Pro customers:**
   - Open ticket in Salesforce with severity level
   - If not resolved within SLA window, reply to ticket requesting escalation
   - Use keyword "ESCALATE" in subject line

2. **For Enterprise customers:**
   - Use dedicated Slack channel: #enterprise-support
   - Or call PagerDuty hotline
   - On-call engineer responds within 15 minutes (Critical issues)

**Severity Definitions:**

| Severity | Definition | Example |
|----------|------------|---------|
| Critical | Platform unavailable | All inference requests failing |
| High | Major feature impaired | Single endpoint down |
| Medium | Minor feature impaired | Dashboard slow |
| Low | Cosmetic issue | Typo in error message |

**When Escalating:**
- Critical issues automatically escalate
- If issue not acknowledged within SLA window
- If first response doesn't address the issue
- When issue spans multiple teams (engineering + infrastructure)

**Information to Have Ready:**
- Your account ID and tier
- API key prefix (not full key)
- Timestamps with timezone
- Error messages or logs
- Steps to reproduce

---

## Section 6: Troubleshooting FAQs

### FAQ 6.1: Why am I getting authentication errors?

**Question:** "My API calls are returning 401 errors. What could be wrong?"

**Answer:**

401 (Unauthorized) errors have several possible causes:

**Common Causes:**

1. **Expired or invalid API key**
   - Verify key is active in Dashboard > API Keys
   - Check if key was deleted or rotated

2. **Incorrect Authorization header format**
   ```http
   # Correct
   Authorization: Bearer nx_live_xxxxx
   
   # Incorrect
   Authorization: nx_live_xxxxx
   ```

3. **OAuth token issues (Enterprise)**
   - OAuth tokens expire after 1 hour
   - Refresh token flow required
   ```python
   # Refresh OAuth token
   POST /api/v2/oauth/refresh
   { "refresh_token": "xxx" }
   ```

4. **Missing permissions**
   - Some endpoints require specific tier permissions
   - Verify your plan includes the endpoint you're calling

5. **IP allowlist blocking**
   - Enterprise customers with IP allowlist enabled
   - Check if request IP is in allowed list

**Diagnostic Steps:**
1. Verify API key in dashboard matches what you're using
2. Test with a simple endpoint: `GET /api/v2/status`
3. Check that Authorization header is properly formatted
4. Review error body for specific error code

**Common Error Codes:**

| Code | Meaning |
|------|---------|
| `AUTH_INVALID_KEY` | API key not found or revoked |
| `AUTH_EXPIRED_TOKEN` | OAuth token expired |
| `AUTH_MISSING_SCOPE` | Insufficient permissions |
| `AUTH_IP_BLOCKED` | IP not in allowlist |

---

### FAQ 6.2: How do I diagnose high error rates?

**Question:** "I'm seeing elevated error rates (4xx/5xx) on my inference requests. How do I diagnose?"

**Answer:**

High error rates can indicate issues on your side or ours. Here's a diagnostic framework:

**Step 1: Check Error Types**

| Error Type | Likely Cause | Your Action |
|------------|-------------|-------------|
| 4xx errors | Client issue | Review request format |
| 429 errors | Rate limiting | Implement backoff |
| 5xx errors | Server issue | Contact support |
| Timeout | Network or load | Retry with backoff |

**Step 2: Check System Status**
- Visit https://status.nexlify.com
- Check for ongoing incidents
- Subscribe to status page updates

**Step 3: Review Your Request Patterns**
```python
# Common 4xx errors and fixes
# 400 Bad Request: Check payload format
# 401 Unauthorized: Verify API key
# 403 Forbidden: Check permissions/scopes
# 422 Unprocessable: Check request body validation
# 429 Too Many: Implement rate limit handling
```

**Step 4: Enable Debug Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# This will log full request/response for debugging
```

**Step 5: Contact Support If:**
- Error rate exceeds your SLA threshold
- 5xx errors persist >5 minutes
- Errors affect specific endpoints only
- Sudden spike in errors with no pattern change

**Information to Include in Support Ticket:**
- Time range of elevated errors
- Specific endpoint(s) affected
- Error code and message samples
- Your account ID
- Request volume during affected period

---

### FAQ 6.3: My model deployment is stuck. What do I do?

**Question:** "I submitted a model deployment yesterday and it's still showing 'deploying' status. What's wrong?"

**Answer:**

Model deployment typically completes in 5-15 minutes. If stuck longer, here are potential causes and solutions:

**Normal Deployment Timeline:**
- Small models (<1GB): 2-5 minutes
- Medium models (1-10GB): 5-15 minutes
- Large models (>10GB): 15-30 minutes

**If Deployment Stuck >30 Minutes:**

1. **Check Deployment Status:**
   ```http
   GET /api/v2/models/{model_id}/deployment
   ```

2. **Check for Errors:**
   ```http
   GET /api/v2/models/{model_id}/logs
   ```

3. **Common Stuck Deployment Causes:**

| Cause | Symptom | Solution |
|-------|---------|----------|
| GPU capacity | Queue position increasing | Wait or retry later |
| Invalid model format | Error in logs | Fix format, redeploy |
| Insufficient storage | Deployment fails at 95% | Free storage |
| Network timeout | No logs updating | Retry deployment |

4. **Cancel and Redeploy:**
   ```http
   DELETE /api/v2/models/{model_id}/deployments/{deployment_id}
   # Then redeploy fresh
   ```

5. **Contact Support If:**
   - Deployment stuck >2 hours
   - Error logs show undefined error
   - You're unable to cancel

**Preventive Measures:**
- Verify model format before deployment
- Ensure sufficient storage quota
- Deploy during off-peak hours (US night)

---

## Appendix A: Quick Reference Card

**Contact Information:**
- General Support: support@nexlify.com
- Enterprise Support: enterprise-support@nexlify.com
- Security Issues: security@nexlify.com (PGP preferred)
- Phone (Pro/Enterprise): +1-888-NEXL-SUP

**Status Page:** https://status.nexlify.com

**API Base URL:** https://api.nexlify.com/v2

**Salesforce Case Types:**
- Billing Inquiry
- Technical Issue
- SLA Credit Request
- Feature Request
- Security - Confidential
- Account Management

---

*Document Owner: Customer Success Team*
*Last Updated: January 15, 2026*
*Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*

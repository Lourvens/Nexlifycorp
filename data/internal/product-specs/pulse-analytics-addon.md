# Pulse Analytics Add-on — Specification

**Status:** GENERAL AVAILABILITY (GA)
**Version:** 1.0
**Last Updated:** May 2026

---

## Overview

Pulse is a real-time analytics add-on for the Nexlify Corp Platform, providing inference metrics, cost tracking, and performance monitoring for production AI workloads.

*Approved by: Dr. Sarah Kim, CPO*

---

## 1. Product Overview

### 1.1 Purpose

Pulse enables platform users to:
- Monitor real-time inference metrics
- Track token consumption and API usage
- Attribute costs by team, project, and model
- Configure custom alerts for anomaly detection
- Optimize inference performance and cost

### 1.2 Target Users

- ML Engineers monitoring production systems
- Finance teams tracking AI costs
- Engineering managers overseeing platform usage
- DevOps teams managing alert thresholds

### 1.3 Pricing

| Platform Tier | Pulse Add-on |
|--------------|--------------|
| Enterprise | Included |
| Pro | $99/month |
| Platform | $79/month |
| Starter | $49/month |
| Free | Not available |

---

## 2. Feature Specification

### 2.1 Real-time Dashboard

**Description:** Live view of inference metrics across all deployed models.

**Metrics Displayed:**
| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| Requests/min | API request rate | Real-time |
| P50/P95/P99 Latency | Response time distribution | 1 minute |
| Error Rate | Failed requests as percentage | 1 minute |
| Token Throughput | Input + output tokens/second | Real-time |
| GPU Utilization | Accelerator utilization percentage | 10 seconds |
| Queue Depth | Pending requests | Real-time |

**Time Range Options:** 1h, 6h, 24h, 7d, 30d, custom

### 2.2 Cost Attribution

**Description:** Granular tracking of API consumption and associated costs.

**Capabilities:**
- Per-API-key cost tracking
- Per-project cost aggregation
- Per-model cost breakdown
- Historical cost trending
- Budget alerts at thresholds

**Cost Components:**
- Input tokens (per 1M)
- Output tokens (per 1M)
- Compute time (per GPU-minute)
- Storage (per GB-day)

**Example Usage Report:**
```json
{
  "project": "production-rag",
  "period": "2026-05",
  "total_cost": 1247.83,
  "breakdown": {
    "claude-3-sonnet": 892.15,
    "claude-3-haiku": 355.68
  },
  "api_calls": 45032,
  "tokens_used": 125000000
}
```

### 2.3 Custom Alert Configuration

**Description:** User-defined alerts on metric thresholds.

**Alert Types:**
| Type | Trigger Condition |
|------|-------------------|
| Latency | P99 > X ms for Y minutes |
| Error Rate | Errors > X% for Y minutes |
| Cost | Daily cost exceeds $X |
| Usage | Monthly tokens exceed X |
| Availability | Success rate < X% |

**Notification Channels:**
- Email (to configured addresses)
- Webhook (POST to URL with JSON payload)
- Slack (via webhook integration)
- PagerDuty (for critical alerts)

### 2.4 Model Performance Analysis

**Description:** Deep dive into model-level performance metrics.

**Analysis Features:**
- Latency distribution histograms
- Token efficiency metrics
- Cache hit rate (for repeated queries)
- Model comparison side-by-side
- Bottleneck identification

### 2.5 Team Management

**Description:** Organize users and assign cost centers.

**Capabilities:**
- Team creation and membership
- Project assignment per team
- Cost center tagging
- Spending limits per team
- Role-based access (viewer, editor, admin)

---

## 3. API Specification

### 3.1 Pulse REST API

**Base URL:** `https://api.nexlifycorp.com/v1/pulse`

**Authentication:** Bearer token with pulse scope

### 3.2 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Current metrics snapshot |
| GET | `/metrics/historical` | Historical metric data |
| GET | `/costs` | Cost summary |
| GET | `/costs/by-project` | Per-project costs |
| GET | `/alerts` | List configured alerts |
| POST | `/alerts` | Create new alert |
| PUT | `/alerts/{alert_id}` | Update alert |
| DELETE | `/alerts/{alert_id}` | Delete alert |
| GET | `/teams` | List teams |
| POST | `/teams` | Create team |

### 3.3 Webhook Payload Format

```json
{
  "alert_type": "latency_threshold",
  "severity": "warning",
  "timestamp": "2026-05-15T14:32:00Z",
  "metric": {
    "name": "p99_latency",
    "value": 450,
    "threshold": 300,
    "unit": "ms"
  },
  "project": "prod-inference",
  "model": "claude-3-sonnet"
}
```

---

## 4. Data Retention

| Plan Tier | Hot Storage | Cold Storage |
|-----------|-------------|--------------|
| Free | 1 day | — |
| Starter | 7 days | — |
| Platform | 30 days | 90 days |
| Pro | 90 days | 1 year |
| Enterprise | 1 year | 3 years |

---

## 5. Performance Specifications

| Metric | Specification |
|--------|---------------|
| Dashboard Latency | < 2 seconds for 24h data |
| Metric Resolution | 10-second granularity |
| Historical Query | < 5 seconds for 30-day range |
| Real-time Update | < 1 second latency |

---

## 6. Integration

### 6.1 Platform Integration

Pulse integrates with:
- Platform API for usage data collection
- NEXL-X3 for hardware metrics
- NEXL-SW for CLI access

### 6.2 External Integrations

| Integration | Capability |
|-------------|------------|
| Grafana | Metrics export via Prometheus |
| Datadog | Logs and metrics export |
| Slack | Alert notifications |
| PagerDuty | Critical alert routing |

---

## 7. SLA

Pulse availability SLA is tied to the underlying Platform tier:

| Platform Tier | Pulse Availability |
|--------------|-------------------|
| Free | 99.0% |
| Starter | 99.5% |
| Platform | 99.9% |
| Pro | 99.95% |
| Enterprise | 99.99% |

---

## 8. Support

- Documentation: docs.nexlifycorp.com/pulse
- Support: support.nexlifycorp.com
- Status Page: status.nexlifycorp.com

**Contact:** James Rodriguez, VP Sales

---

*Document Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
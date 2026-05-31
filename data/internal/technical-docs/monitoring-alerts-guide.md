# Monitoring and Alerts Guide

## Overview

Nexlify Corp provides a comprehensive observability stack for monitoring infrastructure, application performance, and business metrics. This guide covers the monitoring architecture, alert configuration, and operational best practices.

## Observability Stack

| Tool | Purpose | Access |
|------|---------|--------|
| Prometheus | Metrics collection | Dashboard |
| Grafana | Dashboards and visualization | Dashboard |
| Loki | Log aggregation | Dashboard |
| Tempo | Distributed tracing | Dashboard |
| Jaeger | Request tracing | Dashboard |

## Infrastructure Monitoring

### Key Metrics

#### Compute (EKS)

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `cpu_utilization` | CPU usage percentage | > 80% alert |
| `memory_utilization` | Memory usage percentage | > 85% alert |
| `pod_restarts` | Pod restart count | > 5 per hour alert |
| `pod_status` | Pod running/pending/failed | Any failed alert |

#### Database (PostgreSQL)

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `db_connections` | Active database connections | > 80% max alert |
| `db_cpu_utilization` | Database CPU usage | > 70% alert |
| `db_disk_usage` | Disk usage percentage | > 75% alert |
| `query_latency_p99` | 99th percentile query time | > 500ms alert |

#### Cache (Redis)

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `redis_memory_usage` | Memory usage percentage | > 85% alert |
| `redis_connections` | Active connections | > 90% max alert |
| `cache_hit_rate` | Cache hit ratio | < 80% alert |
| `redis_latency` | Command latency p99 | > 50ms alert |

#### Vector Store (Qdrant)

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `qdrant_collections` | Number of collections | Monitor |
| `qdrant_disk_usage` | Disk usage | > 70% alert |
| `search_latency_p99` | Vector search latency | > 200ms alert |

### Infrastructure Alerts

```yaml
groups:
  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: cpu_utilization > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is {{ $value }}% for more than 5 minutes"

      - alert: MemoryPressure
        expr: memory_utilization > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Memory pressure detected"
          description: "Memory usage is {{ $value }}%"
```

## Application Monitoring

### API Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `http_requests_total` | Total HTTP requests | Monitor |
| `http_request_duration_seconds` | Request latency histogram | p99 > 500ms alert |
| `http_requests_errors_total` | Error count by status | > 1% alert |
| `api_uptime` | API availability percentage | < 99.9% alert |

### Request Latency SLOs

| Percentile | Target |
|------------|--------|
| p50 | < 100ms |
| p90 | < 250ms |
| p95 | < 350ms |
| p99 | < 500ms |

### Error Rate Targets

| Error Type | Target |
|------------|--------|
| 4xx errors | < 5% |
| 5xx errors | < 0.1% |
| Total errors | < 5% |

## Rate Limiting Monitoring

### Rate Limit Metrics

Track rate limit consumption across plans:

| Plan | Limit (RPM) | Alert Threshold |
|------|-------------|-----------------|
| Free | 60 | > 80% |
| Starter | 300 | > 80% |
| Platform | 1,000 | > 80% |
| Pro | 3,000 | > 80% |
| Enterprise | 10,000 | > 90% |

### Rate Limit Alerts

```yaml
- alert: RateLimitWarning
  expr: rate_limit_utilization > 0.8
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High rate limit utilization"
    description: "{{ $labels.plan }} plan at {{ $value | humanizePercentage }} capacity"
```

### Endpoint-Specific Monitoring

Special monitoring for endpoint-specific limits:

| Endpoint | Limit | Alert |
|----------|-------|-------|
| `/api/v2/inference` | 100 RPM | > 80% utilization |
| `/api/v2/training` | 50 RPM | > 80% utilization |

## GPU Monitoring

### GPU Job Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `gpu_jobs_running` | Currently running jobs | > 90% capacity |
| `gpu_utilization` | GPU utilization percentage | > 90% alert |
| `gpu_memory_usage` | GPU memory usage | > 85% alert |
| `gpu_temperature` | GPU temperature | > 85°C alert |

### GPU Limits by Version

| Version | Max Concurrent Jobs per Region |
|---------|------------------------------ |
| Before v3.2 | 50 |
| v3.2 and after | 100 |

## Log Monitoring

### Log Aggregation (Loki)

#### Key Log Sources

- Application logs
- Access logs
- Error logs
- Audit logs

#### Log Query Examples

```logql
# Error logs in last 5 minutes
{app="nexlify-api"} |= "error"

# Slow requests
{app="nexlify-api"} | json | duration > 5

# Rate limit hits
{app="nexlify-gateway"} |= "429"
```

### Log Retention

| Log Type | Retention Period |
|----------|-----------------|
| Application logs | 30 days |
| Access logs | 90 days |
| Audit logs | 1 year |
| Error logs | 90 days |

## Distributed Tracing

### Tempo Configuration

Traces collected via Tempo for:

- Request flow analysis
- Latency breakdown
- Error tracing
- Service dependencies

### Jaeger Integration

Use Jaeger for detailed request tracing:

1. Access Jaeger UI
2. Search by trace ID
3. Analyze span timeline
4. Identify bottlenecks

## Alert Configuration

### Alert Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| Critical | Service down or data loss | Immediate |
| High | Major functionality impaired | < 15 minutes |
| Medium | Minor functionality affected | < 1 hour |
| Low | Informational | Next business day |

### Notification Channels

| Channel | Use Case |
|---------|----------|
| PagerDuty | Critical and High severity |
| Slack #alerts | All alert severities |
| Email | Medium and Low severity |

### Alert Rules

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: APIServerErrorRate
        expr: rate(http_requests_errors_total{status=~"5.."}[5m]) > 0.001
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate"
          description: "5xx error rate is {{ $value | humanizePercentage }}"

      - alert: APILatencyDegraded
        expr: histogram_quantile(0.99, http_request_duration_seconds) > 0.5
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "API latency degraded"
          description: "p99 latency is {{ $value }}s"
```

## Dashboards

### Available Dashboards

| Dashboard | Description |
|-----------|-------------|
| Infrastructure Overview | System-wide health at a glance |
| API Performance | Request rates, latency, errors |
| Rate Limiting | Usage by plan, endpoint limits |
| GPU Fleet | GPU utilization, job status |
| Database | Connection pool, query performance |
| Cache Performance | Hit rates, memory usage |
| Vector Store | Collection stats, search latency |

### Dashboard Variables

Common filter variables:
- `region`: us-east-1, us-west-2, eu-west-1, ap-southeast-1
- `environment`: production, staging
- `service`: api, worker, scheduler

## Incident Response

### Incident Severity Classification

| Severity | Impact | Example |
|----------|--------|---------|
| SEV1 | Complete outage | API unavailable |
| SEV2 | Major feature broken | Authentication failing |
| SEV3 | Minor feature impact | Rate limiting errors |
| SEV4 | Minimal impact | Single region degraded |

### Incident Workflow

1. **Detect** - Alert triggered or user reported
2. **Assess** - Determine severity and impact
3. **Communicate** - Notify stakeholders via Slack
4. **Mitigate** - Implement fix or workaround
5. **Resolve** - Confirm service restored
6. **Review** - Post-mortem analysis

### Runbooks

| Incident Type | Runbook |
|---------------|---------|
| API outage | [API Outage Runbook](./runbooks/api-outage.md) |
| Database issues | [Database Runbook](./runbooks/database.md) |
| Rate limit spike | [Rate Limiting Runbook](./runbooks/rate-limiting.md) |
| GPU cluster issues | [GPU Cluster Runbook](./runbooks/gpu-cluster.md) |

## SLAs and SLOs

### Service Level Objectives

| Service | Availability SLO | Latency SLO |
|---------|-----------------|-------------|
| API | 99.95% | p99 < 500ms |
| Vector Search | 99.9% | p99 < 200ms |
| Webhooks | 99.5% | Delivery < 5s |

### SLO Monitoring

```yaml
# SLO dashboard configuration
groups:
  - name: slos
    rules:
      - alert: APISLOBreach
        expr: api_uptime < 0.9995
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "API SLO breach"
          description: "API availability is {{ $value | humanizePercentage }}"
```

## Deployment Monitoring

During deployment, monitor:

1. **Error rate** - Should not increase
2. **Latency** - Should remain stable
3. **Pod status** - All pods running
4. **Log patterns** - No new error patterns

See [Deployment Guide](./deployment-guide.md) for deployment window schedule (Tuesday-Thursday, 10 AM - 4 PM PST).

## Monitoring Setup

### Quick Start

1. Access Grafana at `https://grafana.nexlify.com`
2. Select appropriate dashboard
3. Set alert notifications in Alertmanager
4. Configure PagerDuty integration

### Custom Alerts

Create custom alerts via Prometheus rules:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: custom-alerts
spec:
  groups:
    - name: custom
      rules:
        - alert: CustomMetricAlert
          expr: custom_metric > threshold
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Custom alert"
```
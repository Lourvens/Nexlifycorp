# Deployment Guide

## Overview

This guide covers the deployment procedures, schedules, and best practices for Nexlify Corp infrastructure and services.

## Deployment Window

### Schedule

| Day | Time (PST) |
|-----|-------------|
| Tuesday | 10:00 AM - 4:00 PM |
| Wednesday | 10:00 AM - 4:00 PM |
| Thursday | 10:00 AM - 4:00 PM |

> **Note**: Deployments outside these windows require approval from the Platform team and may incur additional costs.

### Deployment Lead Time

- **Standard deployments**: Minimum 48 hours notice
- **Critical security patches**: 2 hours notice with approval
- **Emergency hotfixes**: Immediate with post-deployment review

## Pre-Deployment Checklist

### Required Checks

- [ ] All tests passing in CI/CD pipeline
- [ ] Code review approved by at least 2 reviewers
- [ ] Database migrations tested in staging
- [ ] Rollback plan documented
- [ ] Deployment notification sent to #deployments channel
- [ ] On-call engineer confirmed available

### Technical Prerequisites

- [ ] Docker images built and pushed to ECR
- [ ] Helm charts updated with new version
- [ ] Kubernetes manifests validated
- [ ] Feature flags configured
- [ ] Environment variables updated

## Infrastructure Deployment

### Kubernetes (EKS)

All services run on Amazon EKS. Deployments use Helm charts:

```bash
# Update Helm repo
helm repo update

# Deploy application
helm upgrade --install nexlify-api ./charts/nexlify-api \
  --namespace production \
  --set image.tag=v2.3.0 \
  --values ./values/production.yaml

# Verify deployment
kubectl rollout status deployment/nexlify-api -n production
```

### Region Deployment Order

Deploy to regions in this order to minimize impact:

1. `us-east-1` (primary)
2. `us-west-2`
3. `eu-west-1`
4. `ap-southeast-1`

Monitor metrics after each regional deployment before proceeding.

## Application Deployment

### API Deployment

The Nexlify Corp API is deployed via GitHub Actions:

1. Tag created with version (e.g., `v2.3.0`)
2. CI pipeline builds Docker image
3. Image pushed to Amazon ECR
4. Helm deployment triggered
5. Smoke tests run against deployed environment
6. Monitoring verified

### Zero-Downtime Deployment

All deployments use rolling updates to ensure zero downtime:

```yaml
# Kubernetes deployment strategy
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
```

## Database Migrations

### Pre-Migration

1. Create backup snapshot
2. Test migration on staging database
3. Verify rollback procedure
4. Schedule maintenance window if needed

### Running Migrations

```bash
# Run pending migrations
alembic upgrade head

# Check migration status
alembic current
alembic history --verbose

# Rollback if needed
alembic downgrade -1
```

### Post-Migration

1. Verify data integrity
2. Run integration tests
3. Monitor error rates
4. Confirm application functionality

## Configuration Management

### Environment Variables

All environment-specific configuration is managed via Kubernetes secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: nexlify-api-config
  namespace: production
type: Opaque
stringData:
  DATABASE_URL: "postgresql://..."
  REDIS_URL: "redis://..."
  API_KEY: "nx_live_xxx"
```

### Secrets Management

Secrets are managed via HashiCorp Vault:

```bash
# Retrieve secret
vault kv get -format=json secret/nexlify/production/api

# Update secret
vault kv put secret/nexlify/production/api API_KEY="nx_live_xxx"
```

## Monitoring During Deployment

### Key Metrics to Watch

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate | > 1% | Rollback |
| Latency p99 | > 500ms | Investigate |
| CPU usage | > 80% | Scale up |
| Memory usage | > 85% | Investigate |

### Observability Stack

During deployment, monitor via:

- **Grafana**: Real-time dashboards
- **Prometheus**: Metrics collection
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing
- **Jaeger**: Request tracing

## Rollback Procedures

### Application Rollback

```bash
# Rollback to previous version
helm rollback nexlify-api production

# Verify rollback
kubectl rollout status deployment/nexlify-api -n production
```

### Database Rollback

```bash
# Rollback migration
alembic downgrade -1

# Restore from backup if needed
pg_restore -h database.nexlify.com -U nexlify -d production backup.dump
```

## Post-Deployment Verification

### Checklist

- [ ] All pods running the new version
- [ ] Error rate within normal bounds
- [ ] Latency within SLA
- [ ] No increased rate limit errors
- [ ] Logs showing expected patterns
- [ ] Integration tests passing

### Sign-Off

Deployment requires sign-off from:

1. On-call engineer
2. Team lead (for major releases)
3. Product owner (for significant features)

## Deployment Environments

| Environment | Purpose | Deployment Frequency |
|-------------|---------|---------------------|
| Development | Local development | On-demand |
| Staging | Pre-production testing | Every commit to main |
| Production | Live users | Weekly (or per release) |

## Contact

For deployment issues:
- Slack: #deployments
- On-call: PagerDuty rotation
- Email: platform-team@nexlify.com
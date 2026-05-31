# CI/CD Pipeline Reference

## Overview

Nexlify Corp uses GitHub Actions for continuous integration and deployment. This document describes the CI/CD pipeline structure, workflows, and best practices.

## CI/CD Architecture

### Pipeline Flow

```
Code Commit → Build → Test → Security Scan → Deploy → Verify
     ↓          ↓        ↓         ↓            ↓         ↓
  GitHub    Docker     pytest   Snyk/Semgrep   EKS      Smoke
  Actions   Build      tests    scan           Deploy   Tests
```

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Every PR/push | Build, test, security scan |
| `deploy-staging.yml` | Push to main | Deploy to staging |
| `deploy-production.yml` | Release tag | Deploy to production |
| `weekly-scan.yml` | Weekly schedule | Security vulnerability scan |

## CI Workflow (ci.yml)

### Trigger Conditions

- Every push to any branch
- Every pull request
- Manual trigger via `workflow_dispatch`

### Pipeline Stages

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  lint:
    name: Lint and Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pre-commit
      - run: pre-commit run --all-files

  test:
    name: Unit and Integration Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv pip install -r requirements.txt
      - run: uv run pytest tests/ -v --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install safety bandit
      - run: safety check --json
      - run: bandit -r ./src

  build-image:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [lint, test, security-scan]
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v1
      - name: Build and push
        run: |
          docker build -t nexlify-api:${{ github.sha }} .
          docker push $ECR_REGISTRY/nexlify-api:${{ github.sha }}
```

## Deployment Workflows

### Staging Deployment (deploy-staging.yml)

```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_STAGING_ROLE }}
          aws-region: us-east-1

      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name nexlify-staging
          helm upgrade --install nexlify-api ./charts/nexlify-api \
            --namespace staging \
            --set image.tag=${{ github.sha }} \
            --values ./values/staging.yaml

      - name: Run smoke tests
        run: |
          uv run pytest tests/e2e/smoke_tests.py -v

      - name: Notify deployment
        if: always()
        run: |
          curl -X POST $SLACK_WEBHOOK \
            -d "{\"text\": \"Deployed to staging: ${{ github.sha }}\"}"
```

### Production Deployment (deploy-production.yml)

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    concurrency:
      group: production-deploy
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_PRODUCTION_ROLE }}
          aws-region: us-east-1

      - name: Run database migrations
        run: |
          uv run alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}

      - name: Deploy to all regions
        run: |
          for region in us-east-1 us-west-2 eu-west-1 ap-southeast-1; do
            aws eks update-kubeconfig --name nexlify-prod-$region --region $region
            helm upgrade --install nexlify-api ./charts/nexlify-api \
              --namespace production \
              --set image.tag=${{ github.sha }} \
              --values ./values/production-$region.yaml
          done

      - name: Verify deployment
        run: |
          uv run pytest tests/e2e/production_smoke_tests.py -v

      - name: Create deployment record
        run: |
          curl -X POST https://api.nexlify.com/api/v2/deployments \
            -H "Authorization: Bearer ${{ secrets.API_KEY }}" \
            -d "{\"version\": \"$VERSION\", \"regions\": [\"us-east-1\",\"us-west-2\",\"eu-west-1\",\"ap-southeast-1\"]}"
```

## Test Configuration

### Test Environments

| Environment | Purpose | Data |
|-------------|---------|------|
| Unit tests | Fast feedback | Mocked |
| Integration tests | Service interaction | Test database |
| E2E tests | Full workflow | Staging data |

### Test Coverage Requirements

Minimum 80% code coverage required for:
- Unit tests
- Integration tests

Run coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Pytest Configuration

pytest.ini location: `./pytest.ini`

Markers available:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Security Scanning

### Dependency Scanning

```yaml
- name: Dependency scan
  run: |
    pip install safety
    safety check --json --output=dependency-report.json
```

### SAST (Static Application Security Testing)

```yaml
- name: SAST Scan
  run: |
    pip install bandit
    bandit -r ./src -f json -o bandit-report.json
```

### Container Scanning

```yaml
- name: Container scan
  run: |
    pip install trivy
    trivy image --severity HIGH,CRITICAL $ECR_REGISTRY/nexlify-api:${{ github.sha }}
```

## Build Artifacts

### Docker Image

- **Registry**: Amazon ECR
- **Repository**: `nexlify-api`
- **Tags**: Commit SHA, branch name, version tag

### Helm Charts

- **Storage**: S3 bucket
- **Charts**: Published to Helm repository after build

## Environment Variables

### Required Secrets

| Secret | Description |
|--------|-------------|
| `AWS_STAGING_ROLE` | AWS IAM role for staging |
| `AWS_PRODUCTION_ROLE` | AWS IAM role for production |
| `PRODUCTION_DATABASE_URL` | Database connection string |
| `SLACK_WEBHOOK` | Slack notification webhook |
| `CODECOV_TOKEN` | Code coverage upload token |

## Pipeline Metrics

### Build Performance

| Metric | Target |
|--------|--------|
| CI pipeline duration | < 15 minutes |
| Deployment duration | < 10 minutes |
| Test suite duration | < 10 minutes |

### Quality Gates

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] No critical/high security issues
- [ ] Lint checks passing
- [ ] Smoke tests passing

## Troubleshooting

### Common Issues

#### Build Failures

1. Check GitHub Actions logs
2. Verify Python version matches requirements
3. Ensure Docker build succeeds locally
4. Check for dependency conflicts

#### Test Failures

1. Run tests locally with same configuration
2. Check for flaky tests
3. Verify test isolation
4. Review test data setup

#### Deployment Failures

1. Check kubectl config
2. Verify Helm chart values
3. Check pod status with `kubectl get pods -n production`
4. Review deployment logs

### Debug Commands

```bash
# Check workflow runs
gh run list

# View workflow logs
gh run view <run-id> --log

# Cancel running workflow
gh run cancel <run-id>

# Rerun failed workflow
gh run rerun <run-id>
```

## Pipeline as Code

### File Location

All GitHub Actions workflows are in:

```
.github/workflows/
├── ci.yml
├── deploy-staging.yml
├── deploy-production.yml
└── weekly-scan.yml
```

### Workflow Versions

Pin action versions for security and stability:

```yaml
# Use specific version tags
- uses: actions/checkout@v4      # v4.x stable
- uses: aws-actions/configure-aws-credentials@v4
```

## Notification and Reporting

### Slack Notifications

Deployment notifications sent to `#deployments`:

```json
{
  "text": "Deployment: Nexlify API v2.3.0",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Deployed to Production*
Version: v2.3.0
Regions: 4/4
Status: All systems operational"
      }
    }
  ]
}
```

### Build Status Badges

Display build status in README:

```markdown
[![CI](https://github.com/nexlify/nexlify-api/actions/workflows/ci.yml/badge.svg)](https://github.com/nexlify/nexlify-api/actions/workflows/ci.yml)
[![Deploy](https://github.com/nexlify/nexlify-api/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/nexlify/nexlify-api/actions/workflows/deploy-production.yml)
```
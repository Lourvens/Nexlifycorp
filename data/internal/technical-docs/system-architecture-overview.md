# System Architecture Overview

## Introduction

Nexlify Corp provides a hybrid knowledge base and agentic AI platform that combines SEC EDGAR filings with internal enterprise documents for financial intelligence. This document provides a comprehensive overview of the system's technical architecture.

## High-Level Architecture

The Nexlify Corp platform follows a modular architecture designed for scalability, reliability, and security:

```
[Client Applications] → [API Gateway (Kong Gateway v3.1)] → [Application Services]
                                                                   ↓
                                                    [PostgreSQL 15 (RDS)]
                                                    [Redis 7.2 (ElastiCache)]
                                                    [Qdrant Vector Store]
                                                    [Apache Kafka]
                                                    [S3 Object Storage]
```

## Infrastructure

### Cloud Provider

- **Cloud**: AWS
- **Regions**:
  - `us-east-1` (US East - Northern Virginia)
  - `us-west-2` (US West - Oregon)
  - `eu-west-1` (EU West - Ireland)
  - `ap-southeast-1` (Asia Pacific - Singapore)

### Compute

- **Kubernetes**: Amazon EKS (Elastic Kubernetes Service)
- **Container Orchestration**: EKS manages all application workloads with auto-scaling capabilities

### Data Layer

| Component | Technology | Purpose |
|-----------|------------|----------|
| Primary Database | PostgreSQL 15 (RDS) | Structured data storage, transactional data |
| Cache Layer | Redis 7.2 (ElastiCache) | Session management, caching, rate limiting |
| Vector Store | Qdrant | Semantic search, embeddings storage |
| Object Storage | S3 | Document storage, media files, backups |
| Event Streaming | Apache Kafka | Async messaging, event-driven architecture |

### Security Infrastructure

- **Secrets Management**: HashiCorp Vault
- **API Gateway**: Kong Gateway v3.1

## Application Architecture

### API Layer

- **Base URL**: `https://api.nexlify.com`
- **Current API Version**: v2
- **Deprecated API Version**: v1
  - Key creation stopped: March 1, 2025
  - Standard shutdown: June 1, 2025
  - Enterprise shutdown: September 1, 2025 (with extension available)

### API Gateway

Kong Gateway v3.1 handles:
- Request routing
- Authentication validation
- Rate limiting
- Request/response transformation
- Logging and monitoring

### Backend Services

The platform is built using LangChain and LangGraph for:
- Document extraction and processing
- Semantic search and retrieval
- AI-powered inference
- Agentic workflows

## Data Flow

```
SEC EDGAR Filings / Internal Documents
            ↓
        Extractors
            ↓
        Chunkers
            ↓
        Vector Store (Qdrant)
            ↓
        Retrieval Layer
            ↓
    [Client Applications]
```

### Processing Pipeline

1. **Ingestion**: Documents are fetched from SEC EDGAR or internal sources
2. **Extraction**: Key information is extracted (risk factors, financial statements, etc.)
3. **Chunking**: Documents are split into manageable chunks with metadata
4. **Vectorization**: Chunks are converted to vector embeddings
5. **Storage**: Stored in Qdrant for semantic search
6. **Retrieval**: Vector similarity search enables relevant document retrieval

## Observability Stack

| Tool | Purpose |
|------|----------|
| Prometheus | Metrics collection |
| Grafana | Dashboards and visualization |
| Loki | Log aggregation |
| Tempo | Distributed tracing |
| Jaeger | Request tracing and debugging |

## Key System Types

### Data Source Categories

- `PUBLIC_SEC`: SEC EDGAR filings
- `INTERNAL_NEXLIFY`: Internal Nexlify Corp documents

### Content Types

- `RISK_FACTORS`
- `FINANCIAL_STATEMENTS`
- `MANAGEMENT_DISCUSSION`
- And other financial document types

### Access Levels

- `PUBLIC`: Publicly accessible
- `INTERNAL`: Internal employees
- `CONFIDENTIAL`: Restricted access
- `STRICTLY_CONFIDENTIAL`: Highly restricted

## Regional Distribution

All four regions (`us-east-1`, `us-west-2`, `eu-west-1`, `ap-southeast-1`) support full platform functionality with the following capacity:

- **GPU Fleet**: Max 50 concurrent jobs per region (up to 100 after v3.2)
- Valid GPU counts: 1, 2, 4, 8, 16

## Security

- Secrets managed via HashiCorp Vault
- API authentication required for all endpoints
- Role-based access control (RBAC)
- Encryption in transit (TLS 1.2+) and at rest

## Next Steps

- See [Authentication Guide](./authentication-guide.md) for API authentication details
- See [Rate Limiting Reference](./rate-limiting-reference.md) for rate limit specifications
- See [Python SDK Reference](./python-sdk-reference.md) for SDK usage
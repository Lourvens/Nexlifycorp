# Python SDK Reference

## Overview

The Nexlify Corp Python SDK provides a convenient way to interact with the Nexlify API from Python applications. The SDK handles authentication, request serialization, and error handling.

## Installation

```bash
pip install nexlify-sdk
```

Or with uv:

```bash
uv pip install nexlify-sdk
```

## Quick Start

```python
from nexlify import Client

# Initialize client
client = Client(api_key="nx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# List documents
documents = client.documents.list()

# Get specific document
doc = client.documents.get("doc_12345")

# Search documents
results = client.documents.search(query="risk factors", limit=10)
```

## Version Information

| Version | Status | Notes |
|---------|--------|-------|
| v2.3 | Current | Active development |
| v3.0 | Upcoming | Target: Q3 2026 |

> **Migration Note**: v3.0 will include breaking changes. A migration guide will be published prior to release. Details are TBD.

## Client Initialization

### Basic Setup

```python
from nexlify import Client

# With API key
client = Client(api_key="nx_live_xxxxx")

# With custom base URL
client = Client(
    api_key="nx_live_xxxxx",
    base_url="https://api.nexlify.com"
)

# With timeout configuration
client = Client(
    api_key="nx_live_xxxxx",
    timeout=30,
    max_retries=3
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | Required | Your API key |
| `base_url` | str | `https://api.nexlify.com` | API base URL |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `verify_ssl` | bool | True | SSL verification |

## Authentication

### API Key

```python
client = Client(api_key="nx_live_xxxxx")
```

### OAuth Token

```python
client = Client(
    access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    token_type="Bearer"
)
```

### JWT

```python
client = Client(jwt_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
```

## Documents API

### List Documents

```python
# List all documents
documents = client.documents.list()

# List with filters
documents = client.documents.list(
    category="PUBLIC_SEC",
    limit=50,
    offset=0
)

# List by content type
documents = client.documents.list(
    content_type="RISK_FACTORS",
    access_level="PUBLIC"
)
```

### Get Document

```python
doc = client.documents.get("doc_12345")
print(doc.id, doc.title, doc.content)
```

### Search Documents

```python
# Semantic search
results = client.documents.search(
    query="quarterly earnings",
    limit=20,
    filters={
        "category": "PUBLIC_SEC",
        "year": 2024
    }
)

for result in results:
    print(f"{result.score}: {result.document.title}")
```

### Create Document

```python
doc = client.documents.create(
    title="Q4 Financial Statement",
    content="Full financial statement content...",
    category="INTERNAL_NEXLIFY",
    content_type="FINANCIAL_STATEMENTS",
    metadata={
        "quarter": "Q4",
        "year": 2024
    }
)
```

### Update Document

```python
doc = client.documents.update(
    "doc_12345",
    title="Updated Title",
    metadata={"updated": True}
)
```

### Delete Document

```python
client.documents.delete("doc_12345")
```

## Inference API

### Run Inference

```python
# Text inference
result = client.inference.run(
    prompt="Analyze the risk factors in this document",
    document_id="doc_12345",
    model="claude-3-sonnet"
)

print(result.output)
```

### Inference with GPU

```python
# Use GPU acceleration
result = client.inference.run(
    prompt="Complex analysis requiring GPU",
    document_ids=["doc_1", "doc_2", "doc_3"],
    gpu_count=4,
    model="custom-model"
)
```

#### Valid GPU Counts

- 1 GPU
- 2 GPUs
- 4 GPUs
- 8 GPUs
- 16 GPUs

## Training API

### Start Training Job

```python
job = client.training.start(
    model_name="custom-financial-model",
    training_data=["doc_1", "doc_2", "doc_3"],
    gpu_count=8,
    epochs=100,
    hyperparameters={
        "learning_rate": 0.001,
        "batch_size": 32
    }
)

print(f"Job started: {job.id}")
```

### Check Training Status

```python
status = client.training.status("job_12345")
print(f"Status: {status.state}")
print(f"Progress: {status.progress}%")
```

### List Training Jobs

```python
jobs = client.training.list(
    state="completed",
    limit=10
)
```

## Webhooks

### Register Webhook

```python
webhook = client.webhooks.create(
    url="https://your-server.com/webhook",
    events=["document.created", "document.updated"],
    secret="your-webhook-secret"
)
```

### List Webhooks

```python
webhooks = client.webhooks.list()
```

### Delete Webhook

```python
client.webhooks.delete("webhook_12345")
```

## Error Handling

```python
from nexlify.exceptions import (
    NexlifyError,
    RateLimitError,
    AuthenticationError,
    NotFoundError
)

try:
    doc = client.documents.get("doc_12345")
except AuthenticationError as e:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError as e:
    print("Document not found")
except NexlifyError as e:
    print(f"API error: {e.code} - {e.message}")
```

### Error Types

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `NexlifyError` | Various | Base exception |
| `AuthenticationError` | 401 | Invalid credentials |
| `RateLimitError` | 429 | Rate limit exceeded |
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 400 | Invalid request |
| `ServerError` | 500 | Server error |

## Pagination

### Using Pagination

```python
# Automatic pagination
for doc in client.documents.list_all():
    print(doc.title)

# Manual pagination
docs = client.documents.list(limit=100)
while docs.has_more:
    docs = client.documents.list(
        offset=docs.next_offset,
        limit=100
    )
```

## Async Support

### Async Client

```python
import asyncio
from nexlify import AsyncClient

async def main():
    client = AsyncClient(api_key="nx_live_xxxxx")

    # Concurrent requests
    doc1, doc2 = await asyncio.gather(
        client.documents.get("doc_1"),
        client.documents.get("doc_2")
    )

    await client.close()

asyncio.run(main())
```

## Logging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

client = Client(api_key="nx_live_xxxxx")
```

## Type Definitions

### Core Types

```python
from nexlify.types import (
    Document,
    Chunk,
    ChunkMetadata,
    DataSourceCategory,
    ContentType,
    AccessLevel
)

# DataSourceCategory
category = DataSourceCategory.PUBLIC_SEC  # SEC filings
category = DataSourceCategory.INTERNAL_NEXLIFY  # Internal docs

# ContentType
content_type = ContentType.RISK_FACTORS
content_type = ContentType.FINANCIAL_STATEMENTS
content_type = ContentType.MANAGEMENT_DISCUSSION

# AccessLevel
access_level = AccessLevel.PUBLIC
access_level = AccessLevel.INTERNAL
access_level = AccessLevel.CONFIDENTIAL
access_level = AccessLevel.STRICTLY_CONFIDENTIAL
```

See [typescript-types.json](./typescript-types.json) for complete type definitions.

## Advanced Configuration

### Custom HTTP Client

```python
import httpx
from nexlify import Client

http_client = httpx.Client(
    timeout=60,
    limits=httpx.Limits(max_connections=100)
)

client = Client(
    api_key="nx_live_xxxxx",
    http_client=http_client
)
```

### Proxy Configuration

```python
client = Client(
    api_key="nx_live_xxxxx",
    proxies={
        "http": "http://proxy:8080",
        "https": "https://proxy:8080"
    }
)
```

## Changelog

### v2.3.0

- Added support for GPU inference jobs
- Improved error messages
- Added async client support
- Bug fixes and performance improvements

### v2.2.0

- Added webhook management
- Enhanced search functionality
- New pagination options
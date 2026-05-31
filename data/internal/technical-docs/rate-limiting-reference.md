# Rate Limiting Reference

## Overview

Nexlify Corp implements rate limiting to ensure fair usage and maintain service stability across all plans. Rate limits are applied per API key and can vary based on your subscription tier.

## Plan-Based Rate Limits

| Plan | Requests per Minute (RPM) |
|------|--------------------------- |
| Free | 60 |
| Starter | 300 |
| Platform | 1,000 |
| Pro | 3,000 |
| Enterprise | 10,000 |

## Endpoint-Specific Limits

In addition to plan-based limits, certain endpoints have specific rate limits:

| Endpoint | Limit Type | Limit |
|----------|------------|-------|
| `/api/v2/inference` | Requests per minute | 100 |
| `/api/v2/training` | Requests per minute | 50 |

> **Note**: Enterprise plan includes both the standard 10,000 RPM limit AND endpoint-specific limits for `/api/v2/inference` (100 RPM) and `/api/v2/training` (50 RPM).

## Rate Limit Headers

Every API response includes rate limit information in headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 3000
X-RateLimit-Remaining: 2995
X-RateLimit-Reset: 1704067260
Retry-After: 60
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed per minute |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the limit resets |
| `Retry-After` | Seconds to wait before retrying (only on 429) |

## Handling Rate Limits

### When Rate Limited

When you exceed your rate limit, the API returns a `429 Too Many Requests` response:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded your rate limit of 3000 requests per minute.",
    "details": {
      "limit": 3000,
      "reset_at": 1704067260,
      "retry_after": 60
    }
  }
}
```

### Best Practices

1. **Implement exponential backoff** - Wait progressively longer between retries
2. **Batch requests** - Combine multiple operations where possible
3. **Monitor usage** - Track `X-RateLimit-Remaining` header
4. **Cache responses** - Reduce unnecessary API calls
5. **Use webhooks** - For real-time updates without polling

### Retry Example

```python
import time
import requests

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        response = func()
        if response.status_code == 429:
            wait_time = int(response.headers.get('Retry-After', 60))
            time.sleep(wait_time * (2 ** attempt))  # Exponential backoff
        else:
            return response
    raise Exception("Max retries exceeded")
```

## GPU Job Limits

### Concurrent Job Limits

| Version | Max Concurrent Jobs per Region |
|---------|------------------------------ |
| Before v3.2 | 50 |
| v3.2 and after | 100 |

### Valid GPU Counts

GPU job requests must use valid GPU counts:

- 1 GPU
- 2 GPUs
- 4 GPUs
- 8 GPUs
- 16 GPUs

## Webhook Rate Limits

Webhooks have separate rate limits based on your plan. See [Webhook Events Reference](./webhook-events-reference.md) for details.

## Monitoring Rate Limits

### Via API

Check your current rate limit status:

```http
GET /api/v2/rate-limit-status
Authorization: nx_live_xxxxx
```

Response:

```json
{
  "plan": "pro",
  "limit": 3000,
  "remaining": 2995,
  "reset_at": 1704067260,
  "endpoint_limits": {
    "/api/v2/inference": {
      "limit": 100,
      "remaining": 98
    },
    "/api/v2/training": {
      "limit": 50,
      "remaining": 50
    }
  }
}
```

## Increasing Rate Limits

To request higher rate limits:

1. **Upgrade your plan** - Higher tiers offer increased limits
2. **Contact enterprise support** - Custom limits available for enterprise
3. **Implement rate limit handling** - Efficient API usage may qualify for limit increases

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `ENDPOINT_RATE_LIMIT_EXCEEDED` | 429 | Endpoint-specific limit exceeded |
| `GPU_LIMIT_EXCEEDED` | 429 | GPU job concurrent limit exceeded |

See [error-codes.json](./error-codes.json) for complete error code documentation.
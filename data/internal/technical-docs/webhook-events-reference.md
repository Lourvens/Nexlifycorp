# Webhook Events Reference

## Overview

Webhooks allow your application to receive real-time notifications when events occur in the Nexlify system. Instead of polling for updates, your server receives HTTP POST requests when notable events happen.

## Webhook Configuration

### Registering a Webhook

```python
webhook = client.webhooks.create(
    url="https://your-server.com/nexlify-webhook",
    events=["document.created", "document.updated", "training.completed"],
    secret="your-webhook-secret"
)
```

### Available Events

| Event | Description |
|-------|-------------|
| `document.created` | New document added |
| `document.updated` | Document content or metadata changed |
| `document.deleted` | Document removed |
| `training.started` | Training job initiated |
| `training.progress` | Training progress update |
| `training.completed` | Training job finished |
| `training.failed` | Training job failed |
| `inference.started` | Inference job started |
| `inference.completed` | Inference job finished |
| `inference.failed` | Inference job failed |

## Webhook Payload Structure

All webhook payloads follow a consistent structure:

```json
{
  "id": "evt_1234567890",
  "type": "document.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "doc_12345",
      "title": "Q4 Financial Statement",
      "category": "INTERNAL_NEXLIFY",
      "created_at": "2025-01-15T10:30:00Z"
    }
  }
}
```

## Event Payload Reference

### document.created

```json
{
  "id": "evt_1234567890",
  "type": "document.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "doc_12345",
      "title": "Q4 Financial Statement",
      "category": "PUBLIC_SEC",
      "content_type": "FINANCIAL_STATEMENTS",
      "access_level": "INTERNAL",
      "size": 45678,
      "created_at": "2025-01-15T10:30:00Z"
    }
  }
}
```

### document.updated

```json
{
  "id": "evt_0987654321",
  "type": "document.updated",
  "timestamp": "2025-01-15T11:00:00Z",
  "data": {
    "object": {
      "id": "doc_12345",
      "title": "Q4 Financial Statement - Revised",
      "changes": ["title", "content"],
      "updated_at": "2025-01-15T11:00:00Z"
    }
  }
}
```

### document.deleted

```json
{
  "id": "evt_5678901234",
  "type": "document.deleted",
  "timestamp": "2025-01-15T12:00:00Z",
  "data": {
    "object": {
      "id": "doc_12345",
      "deleted_at": "2025-01-15T12:00:00Z"
    }
  }
}
```

### training.started

```json
{
  "id": "evt_training_001",
  "type": "training.started",
  "timestamp": "2025-01-15T10:00:00Z",
  "data": {
    "object": {
      "job_id": "job_abc123",
      "model_name": "custom-financial-model",
      "gpu_count": 8,
      "estimated_duration_minutes": 120
    }
  }
}
```

### training.progress

```json
{
  "id": "evt_training_002",
  "type": "training.progress",
  "timestamp": "2025-01-15T10:15:00Z",
  "data": {
    "object": {
      "job_id": "job_abc123",
      "progress_percent": 25,
      "current_epoch": 25,
      "total_epochs": 100,
      "loss": 0.045,
      "accuracy": 0.92
    }
  }
}
```

### training.completed

```json
{
  "id": "evt_training_003",
  "type": "training.completed",
  "timestamp": "2025-01-15T12:00:00Z",
  "data": {
    "object": {
      "job_id": "job_abc123",
      "model_name": "custom-financial-model",
      "final_loss": 0.023,
      "final_accuracy": 0.95,
      "artifacts": {
        "model_checkpoint": "s3://nexlify-models/job_abc123/checkpoint",
        "metrics": "s3://nexlify-models/job_abc123/metrics.json"
      }
    }
  }
}
```

### training.failed

```json
{
  "id": "evt_training_004",
  "type": "training.failed",
  "timestamp": "2025-01-15T11:30:00Z",
  "data": {
    "object": {
      "job_id": "job_abc123",
      "error_code": "GPU_ALLOCATION_FAILED",
      "error_message": "Unable to allocate required GPU resources",
      "failed_at": "2025-01-15T11:30:00Z"
    }
  }
}
```

### inference.started

```json
{
  "id": "evt_inference_001",
  "type": "inference.started",
  "timestamp": "2025-01-15T10:00:00Z",
  "data": {
    "object": {
      "job_id": "inf_xyz789",
      "model": "claude-3-sonnet",
      "gpu_count": 4,
      "estimated_duration_seconds": 30
    }
  }
}
```

### inference.completed

```json
{
  "id": "evt_inference_002",
  "type": "inference.completed",
  "timestamp": "2025-01-15T10:00:30Z",
  "data": {
    "object": {
      "job_id": "inf_xyz789",
      "output": "Analysis complete. Key risk factors identified...",
      "processing_time_ms": 2850
    }
  }
}
```

### inference.failed

```json
{
  "id": "evt_inference_003",
  "type": "inference.failed",
  "timestamp": "2025-01-15T10:00:15Z",
  "data": {
    "object": {
      "job_id": "inf_xyz789",
      "error_code": "MODEL_NOT_FOUND",
      "error_message": "Specified model does not exist",
      "failed_at": "2025-01-15T10:00:15Z"
    }
  }
}
```

## Verifying Webhook Signatures

All webhook requests include a signature header for verification:

```http
X-Nexlify-Signature: t=1704067200,v1=abc123...
```

### Verification Process

```python
import hmac
import hashlib
import time

def verify_webhook_signature(payload_body, signature_header, secret):
    if not signature_header:
        return False

    # Parse signature header
    parts = dict(item.split("=") for item in signature_header.split(","))
    timestamp = parts.get("t")
    signature = parts.get("v1")

    # Check timestamp (5 minute window)
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:
        return False

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload_body}"
    expected = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

## Webhook Retry Policy

Failed webhook deliveries are retried with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |

After 5 failed attempts, the webhook delivery is marked as failed and no further retries occur.

## Best Practices

### Security

1. **Verify signatures** - Always validate webhook signatures
2. **Use HTTPS** - Register HTTPS endpoints only
3. **Keep secrets secure** - Rotate webhook secrets periodically
4. **Log webhook requests** - Keep audit trail for debugging

### Reliability

1. **Respond quickly** - Return 200 within 5 seconds
2. **Process asynchronously** - Queue webhook processing
3. **Handle duplicates** - Design idempotent handlers
4. **Monitor failures** - Set up alerts for failed deliveries

### Implementation

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/nexlify-webhook", methods=["POST"])
def handle_webhook():
    # Get signature and body
    signature = request.headers.get("X-Nexlify-Signature")
    body = request.get_data()

    # Verify signature
    if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
        return jsonify({"error": "Invalid signature"}), 401

    # Parse event
    event = request.get_json()

    # Process asynchronously
    process_webhook_event.delay(event)

    return jsonify({"status": "received"}), 200
```

## Rate Limits for Webhooks

Webhook delivery is subject to system rate limits. If your endpoint is slow or unavailable:

1. Retries are attempted per the retry policy
2. Events may be delivered out of order during retries
3. Consider implementing a webhook queue for processing

## Monitoring Webhooks

### Webhook Delivery Status

Check webhook delivery status via API:

```python
deliveries = client.webhooks.deliveries("webhook_12345")
for delivery in deliveries:
    print(f"{delivery.status} - {delivery.attempt_count} attempts")
```

### Metrics

Monitor webhook performance:
- Delivery success rate
- Average delivery time
- Failure reasons
- Retry count

## Testing Webhooks

### Test Event Delivery

```python
# Send test event to your webhook
client.webhooks.test("webhook_12345", event_type="document.created")
```

### Local Testing

Use tools like ngrok or localtunnel for local development:

```bash
ngrok http 5000
# Register https://abc123.ngrok.io/webhook as your webhook URL
```
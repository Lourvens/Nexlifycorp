# SDK v2 to v3 Migration Guide

**Current SDK Version:** v2.3
**Target SDK Version:** v3.0
**Target Release:** Q3 2026

---

## Overview

SDK v3.0 introduces breaking changes to improve type safety, performance, and developer experience. This guide provides the information you need to migrate applications from SDK v2.x to SDK v3.0.

**Important:** SDK v2.3 is the recommended version until SDK v3.0 GA. Do not migrate production workloads until you have tested thoroughly in a non-production environment.

*For detailed breaking changes, see official migration documentation at docs.nexlifycorp.com/sdk-migration*

*Approved by: Robert Chen, VP Engineering*

---

## Migration Timeline

| Date | Milestone |
|------|-----------|
| Q2 2026 | SDK v3.0 beta available |
| Q3 2026 | SDK v3.0 general availability |
| Q4 2026 | SDK v2.x enters maintenance mode |
| Q1 2027 | SDK v2.x end-of-life |

---

## What's New in SDK v3.0

### Type Safety Improvements

- Stronger TypeScript definitions
- Runtime validation of configuration objects
- Stricter enum types for API parameters

### Performance Enhancements

- Connection pooling by default
- Reduced memory footprint (30% reduction)
- Batch API improvements

### New Features

- Native streaming support
- Enhanced error classification
- Plugin architecture for custom middleware

---

## Breaking Changes

The following breaking changes are confirmed for SDK v3.0. For the complete list of specific API changes, see official migration documentation.

### Configuration Changes

| v2.x | v3.0 | Migration Action |
|------|------|------------------|
| `api_key` | `authentication.key` | Update config structure |
| `timeout_ms` | `timeouts.request` | Nested config |
| `max_retries` | `retryPolicy.maxAttempts` | Renamed and nested |

### API Response Changes

| Change | Description |
|--------|-------------|
| Response envelope | Simplified response structure |
| Error format | New error codes with structured payload |
| Pagination | Cursor-based pagination (replacing offset) |

### Authentication Changes

| v2.x | v3.0 |
|------|------|
| API key in header | API key in config object (no longer header) |
| Single auth method | Multiple auth methods supported |

### Model Invocation Changes

| v2.x | v3.0 |
|------|------|
| `models.generate()` | `inference.generate()` |
| `models.stream()` | `inference.stream()` |
| Sync by default | Async by default; sync available via flag |

---

## Migration Steps

### Step 1: Review Current Usage

Audit your codebase for SDK v2.x usage:
```bash
# Scan for SDK v2 imports
grep -r "nexlify-sdk" --include="*.ts" .
grep -r "from.*nexlify" --include="*.py" .
```

### Step 2: Update Configuration

Update your initialization code:

**Before (v2.x):**
```typescript
import { NexlifyClient } from '@nexlify/sdk';

const client = new NexlifyClient({
  api_key: 'your-api-key',
  timeout_ms: 30000,
  max_retries: 3
});
```

**After (v3.0):**
```typescript
import { NexlifyClient } from '@nexlify/sdk';

const client = new NexlifyClient({
  authentication: {
    key: 'your-api-key'
  },
  timeouts: {
    request: 30000
  },
  retryPolicy: {
    maxAttempts: 3
  }
});
```

### Step 3: Update API Calls

Update method calls to use new naming conventions:

**Before (v2.x):**
```typescript
const response = await client.models.generate({
  model: 'claude-3-sonnet',
  prompt: 'Hello'
});
```

**After (v3.0):**
```typescript
const response = await client.inference.generate({
  model: 'claude-3-sonnet',
  prompt: 'Hello'
});
```

### Step 4: Update Error Handling

Update try/catch blocks for new error format:

**Before (v2.x):**
```typescript
try {
  await client.models.generate({ ... });
} catch (error) {
  if (error.code === 'RATE_LIMIT') {
    // handle rate limit
  }
}
```

**After (v3.0):**
```typescript
try {
  await client.inference.generate({ ... });
} catch (error) {
  if (error instanceof RateLimitError) {
    // handle rate limit
  } else if (error instanceof TimeoutError) {
    // handle timeout
  }
}
```

### Step 5: Update Pagination (if applicable)

If you use pagination, update to cursor-based:

**Before (v2.x):**
```typescript
const page = await client.models.list({
  offset: 0,
  limit: 100
});
```

**After (v3.0):**
```typescript
const page = await client.inference.list({
  cursor: null,
  limit: 100
});
// Use page.nextCursor for subsequent pages
```

### Step 6: Test Thoroughly

Run your test suite against SDK v3.0 beta:
```bash
npm install @nexlify/sdk@3.0.0-beta
```

---

## Deprecation Notices

### SDK v2.x Deprecations (Effective Q3 2026)

The following will be removed in SDK v3.0 and should not be used:

| Deprecated API | Replacement | Removal Date |
|---------------|-------------|---------------|
| `client.connect()` | Remove (automatic) | Q4 2026 |
| `models.stream()` sync mode | `inference.stream()` async | Q4 2026 |
| `client.close()` | Remove (automatic cleanup) | Q4 2026 |

---

## Compatibility Mode

A compatibility layer will be available during the transition period (Q3-Q4 2026) to ease migration:

```typescript
import { NexlifyClient } from '@nexlify/sdk';
import { compatibilityMode } from '@nexlify/sdk/compat';

const client = new NexlifyClient({
  ...compatibilityMode.v2()
});
```

**Note:** Compatibility mode will be removed in Q1 2027. Plan your migration accordingly.

---

## Testing Recommendations

1. **Unit Tests:** Run existing tests with SDK v3.0 beta
2. **Integration Tests:** Verify API call patterns
3. **Load Tests:** Confirm performance improvements
4. **Error Handling:** Test all error paths

---

## Getting Help

- **Migration Documentation:** docs.nexlifycorp.com/sdk-migration
- **Migration Support:** support@nexlifycorp.com
- **Community Forum:** community.nexlifycorp.com

---

## Contact

For migration assistance, contact:
- **Technical Account Manager:** Your assigned TAM
- **VP Engineering:** Robert Chen

---

*Document Classification: INTERNAL — LEVEL 2 CONFIDENTIAL*
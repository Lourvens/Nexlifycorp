# Authentication Guide

## Overview

The Nexlify Corp API supports three authentication methods to accommodate different use cases:

1. **API Key Authentication** - For server-to-server communication
2. **OAuth 2.0** - For user-authorized applications
3. **JWT (JSON Web Tokens)** - For stateless authentication

## API Key Authentication

### Key Prefixes

Nexlify Corp uses prefixed API keys to identify key type:

| Prefix | Environment | Description |
|--------|-------------|-------------|
| `nx_live_` | Production | Live API keys for production use |
| `nx_test_` | Testing | Test API keys for development/testing |
| `nx_dev_` | Development | Developer keys for local development |

### Key Format

```
nx_live_<random_string>
nx_test_<random_string>
nx_dev_<random_string>
```

### Usage

Include the API key in the `Authorization` header:

```http
GET /api/v2/documents HTTP/1.1
Host: api.nexlify.com
Authorization: nx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or via query parameter:

```http
GET /api/v2/documents?api_key=nx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Key Lifecycle

| Milestone | Date |
|-----------|------|
| v1 Key Creation Stops | March 1, 2025 |
| v1 Standard Shutdown | June 1, 2025 |
| v1 Enterprise Shutdown | September 1, 2025 |

> **Note**: Enterprise customers may request an extension for the v1 shutdown deadline.

## OAuth 2.0

### Authorization Code Flow

Recommended for applications with a server-side component.

```
1. User initiates auth → Redirect to Nexlify authorization URL
2. User grants permission → Redirect back with authorization code
3. Exchange code for tokens → POST to token endpoint
4. Receive access + refresh tokens
5. Use access token for API calls
```

### Endpoints

| Endpoint | URL |
|----------|-----|
| Authorization | `https://api.nexlify.com/oauth/authorize` |
| Token | `https://api.nexlify.com/oauth/token` |
| Revoke | `https://api.nexlify.com/oauth/revoke` |

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

### Scopes

| Scope | Description |
|-------|-------------|
| `read:documents` | Read document content |
| `write:documents` | Create/update documents |
| `read:users` | Read user information |
| `admin` | Administrative operations |

## JWT Authentication

### Token Structure

JWT tokens contain three parts: header, payload, and signature.

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_12345",
    "org": "nexlify_corp",
    "scopes": ["read:documents", "write:documents"],
    "iat": 1704067200,
    "exp": 1704070800
  }
}
```

### Validation

JWT tokens must be validated by:
1. Verifying signature with public key
2. Checking expiration (`exp` claim)
3. Validating issuer (`iss` claim)
4. Checking audience (`aud` claim)

### Generating JWTs

```python
import jwt

payload = {
    "sub": "user_12345",
    "org": "nexlify_corp",
    "scopes": ["read:documents"],
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

token = jwt.encode(payload, private_key, algorithm="RS256")
```

## Multi-Factor Authentication (MFA)

Enterprise plans support MFA for additional security:

- TOTP (Time-based One-Time Password)
- SMS-based verification
- Hardware security keys (FIDO2)

Enable MFA via the dashboard or API.

## API Versioning

### Current and Deprecated Versions

| Version | Status | End of Life |
|---------|--------|-------------|
| v2 | Current | Active |
| v1 | Deprecated | June 1, 2025 (standard) / September 1, 2025 (enterprise) |

### Version Selection

Specify version in the request path:

```
https://api.nexlify.com/api/v2/documents
https://api.nexlify.com/api/v1/documents
```

## Security Best Practices

1. **Never expose API keys in client-side code**
2. **Use environment variables for key storage**
3. **Rotate keys periodically**
4. **Use the minimum required scopes**
5. **Implement proper key storage** (HashiCorp Vault recommended)
6. **Monitor API usage** for anomalies

## Error Responses

Authentication errors return appropriate HTTP status codes:

| Status | Description |
|--------|-------------|
| 401 | Missing or invalid credentials |
| 403 | Valid credentials but insufficient permissions |
| 429 | Rate limit exceeded |

See [Error Codes Reference](./error-codes.json) for detailed error codes.
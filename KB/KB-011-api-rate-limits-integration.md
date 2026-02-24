# NimbusAPI Rate Limits and Integration Best Practices

**Article Number:** KB-011  
**Product:** NimbusAPI  
**Category:** API & Developer  
**Last Updated:** February 2026

## Overview

NimbusAPI is the public REST API for the NimbusCloud platform. This article documents rate limits, throttling behavior, webhook configuration, retry strategies, and best practices for building reliable integrations.

## API Rate Limits

### Per-Application Limits
| Plan | Requests/Minute | Requests/Day | Concurrent Connections |
|------|----------------|--------------|----------------------|
| Free | 60 | 10,000 | 5 |
| Business | 300 | 100,000 | 25 |
| Enterprise | 1,000 | 500,000 | 100 |
| Custom | Negotiable | Negotiable | Negotiable |

### Per-Endpoint Limits
Some endpoints have additional limits beyond the application-level rate:

| Endpoint | Additional Limit | Reason |
|----------|-----------------|--------|
| `POST /users` | 50/minute | Prevents bulk account creation abuse |
| `POST /files/upload` | 20/minute | Bandwidth management |
| `GET /search` | 30/minute | Search index load protection |
| `POST /webhooks/test` | 5/minute | Prevents webhook spam |

### Rate Limit Headers
Every API response includes rate limit information:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 247
X-RateLimit-Reset: 1708732800
X-RateLimit-RetryAfter: 0
```

### Throttling Behavior
When you exceed the rate limit:
1. API returns `429 Too Many Requests`
2. `Retry-After` header indicates seconds to wait
3. Continued requests during throttling extend the cooldown period
4. Repeated violations (>10 per hour) may result in temporary suspension (1 hour)

## Webhook Configuration

### Setting Up Webhooks
1. Navigate to NimbusAdmin > Settings > Apps > [your app] > Webhooks
2. Click **Add Webhook Endpoint**
3. Enter the **Endpoint URL** (must be HTTPS)
4. Select **Events** to subscribe to (e.g., `user.created`, `file.uploaded`, `task.completed`)
5. Click **Create** — NimbusCloud sends a verification `POST` with a challenge token
6. Your endpoint must respond with the challenge token to complete verification

### Available Webhook Events
| Category | Events |
|----------|--------|
| Users | `user.created`, `user.updated`, `user.deactivated`, `user.deleted` |
| Files | `file.uploaded`, `file.updated`, `file.deleted`, `file.shared` |
| Tasks | `task.created`, `task.updated`, `task.completed`, `task.deleted` |
| Meetings | `meeting.started`, `meeting.ended`, `meeting.recording_ready` |
| Security | `security.login_failed`, `security.mfa_reset`, `security.api_key_rotated` |

### Webhook Reliability
- NimbusCloud retries failed webhook deliveries up to 5 times with exponential backoff (1, 5, 25, 125, 625 seconds)
- Webhooks that fail consistently (>50% failure rate over 24 hours) are auto-disabled with an admin notification
- Webhook payloads are signed with HMAC-SHA256 — verify the `X-NimbusCloud-Signature` header

## Integration Patterns

### Recommended: Webhook + Polling Hybrid
For critical data synchronization:
1. **Primary**: Use webhooks for real-time notifications
2. **Backup**: Run a polling job every 15 minutes to catch any missed webhook events
3. **Reconciliation**: Daily full sync to ensure data consistency

### Retry Strategy (Exponential Backoff)
```python
import time, random

def api_call_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            jitter = random.uniform(0, retry_after * 0.1)
            time.sleep(retry_after + jitter)
            continue
        return response
    raise Exception("Max retries exceeded")
```

### Batch Operations
For bulk data operations, use batch endpoints instead of individual API calls:
- `POST /api/v2/users/batch` — Create/update up to 100 users per request
- `POST /api/v2/files/batch` — Upload metadata for up to 50 files per request
- `POST /api/v2/tasks/batch` — Create up to 200 tasks per request

Batch endpoints count as a single rate-limited request regardless of items in the batch.

## Common API Issues

### 429 Errors During Peak Sync
**Symptoms:** Nightly SCIM sync or data export jobs hit rate limits.

**Resolution:**
1. Implement exponential backoff with jitter (see code sample above)
2. Use batch endpoints to reduce total request count
3. Spread sync operations across larger time windows instead of bursting
4. Contact NimbusCloud support to request a temporary rate limit increase for migration projects

### Authentication Token Expired
**Symptoms:** API returns `401 Unauthorized` after working previously.

**Resolution:**
1. Check token expiration — access tokens expire after 1 hour
2. Use the refresh token to obtain a new access token (see KB-006)
3. For service accounts (client credentials), request a new token from the token endpoint
4. Verify the client secret hasn't expired: NimbusAdmin > Apps > [app] > Credentials

## API Versioning
NimbusAPI uses URL-based versioning:
- **Current**: `/api/v2/` (stable, recommended)
- **Legacy**: `/api/v1/` (deprecated, sunset December 2026)
- **Preview**: `/api/preview/` (unstable, not for production)

## Best Practices

1. **Implement exponential backoff** on all API calls — never tight-loop on 429 errors
2. **Use webhooks instead of polling** for real-time data needs
3. **Batch operations** where possible to maximize throughput within rate limits
4. **Cache responses** for read-heavy workloads — use `ETag` and `If-None-Match` headers
5. **Migrate to v2 API** before the v1 sunset date
6. **Monitor your usage** — NimbusAdmin > Apps > [app] > Usage Dashboard shows daily request counts

## Related Articles
- KB-006: OAuth 2.0 and OIDC Integration Troubleshooting
- KB-004: NimbusAdmin Tenant and User Provisioning
- KB-012: System Maintenance and Incident Response Playbook

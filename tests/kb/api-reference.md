# API Reference

## Authentication

All API requests require a bearer token:

```
curl -H "Authorization: Bearer $CLOUDPEAK_TOKEN" https://api.cloudpeak.example/v1/projects
```

Create tokens under Account → API Tokens. Tokens can be scoped read-only or read-write and can be revoked at any time. Tokens expire after 90 days by default; Business plan customers can create non-expiring tokens.

## Rate limits

- Starter: 60 requests/minute
- Pro: 300 requests/minute
- Business: 1200 requests/minute

Exceeding the limit returns HTTP 429 with a `Retry-After` header. Rate limits are per-token, not per-account.

## Deployments endpoint

`POST /v1/projects/{id}/deployments` triggers a new deployment from the connected repository's default branch. `GET /v1/projects/{id}/deployments` lists recent deployments with status: `queued`, `building`, `live`, or `failed`.

## Webhooks

Configure webhooks under Project → Settings → Webhooks. Events: `deployment.started`, `deployment.succeeded`, `deployment.failed`. Payloads are signed with HMAC-SHA256; the signature is in the `X-CloudPeak-Signature` header. Webhook deliveries are retried 3 times with exponential backoff.

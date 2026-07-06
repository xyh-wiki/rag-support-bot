# API Reference

## Authentication

API requests use bearer tokens. Create a token from Settings -> Developer -> API tokens. Tokens inherit the permissions of the user who created them.

Example header:

```http
Authorization: Bearer nw_live_xxx
```

## Rate limits

Starter workspaces allow 60 requests per minute. Pro workspaces allow 300 requests per minute. Business workspaces allow 2,000 requests per minute. Rate limits are calculated per token.

When a request exceeds the limit, the API returns HTTP 429 and includes a Retry-After header in seconds.

## Create document endpoint

`POST /v1/documents` creates a document record and queues it for indexing. The request body must include `title`, `space_id`, and either `content` or `source_url`.

The endpoint returns HTTP 202 while indexing is pending. Use `GET /v1/documents/{id}` to check the document status.

## Webhooks

Webhooks can notify external systems when a document is created, indexing finishes, a member is invited, or a billing event occurs. Webhooks are signed with HMAC-SHA256 using the endpoint secret.

If a webhook delivery fails, it is retried for 24 hours with exponential backoff.

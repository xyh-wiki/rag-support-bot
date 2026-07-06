# Troubleshooting

## Site shows 502 Bad Gateway

A 502 error usually means the upstream application is not reachable. Check whether the application process is running, confirm the reverse proxy points to the correct port, and inspect the application logs.

For Docker deployments, run `docker ps` and confirm the container exposes the expected port. For systemd deployments, run `systemctl status northwind-docs`.

## Search returns old content

The search index is refreshed automatically when files change. If old content still appears after one minute, check file permissions and confirm the document directory is writable by the service user.

As a temporary workaround, restart the service to rebuild the index from scratch.

## Invitation email not received

Ask the recipient to check spam and quarantine folders. Invitation emails are sent from no-reply@northwind.example. If the address was mistyped, cancel the pending invite and create a new one.

Business workspaces can configure a custom mail sender through SMTP settings.

## Slow responses

Slow responses are usually caused by very large source excerpts, overloaded completion providers, or network latency to the model gateway. Reduce TOP_K, shorten oversized documents, or switch to a faster model for interactive use.

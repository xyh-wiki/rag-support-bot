# Troubleshooting

## The embedded launcher is not visible

The widget uses a Shadow DOM and injects its component CSS through an inline
`<style>` element. If the host site's CSP has `style-src 'self'` without
`'unsafe-inline'`, the browser can load `widget.js` while refusing the styles
that position the launcher in the bottom-right corner.

For a same-origin reverse proxy, allow:

```http
style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'
```

For cross-origin embedding, add the bot origin to `script-src` and
`connect-src`, then add the host origin to `ALLOWED_ORIGINS` on the bot. Do not
add `'unsafe-inline'` to `script-src`.

Verification checklist:

1. `widget.js` returns HTTP 200.
2. `/api/config` returns HTTP 200.
3. The browser console has no CSP or CORS error.
4. The host page has a `<body>` when the widget script runs.
5. A hard refresh loads the latest host JavaScript after deployment.

## Deployment failed with "build timeout"

Builds are limited to 15 minutes on Starter, 30 minutes on Pro and Business.
Common fixes:

- Cache dependencies: enable build cache under Project → Settings → Build.
- Reduce bundle size: check for accidentally committed large files.
- Upgrade your plan if your build legitimately needs more time.

## Site shows 502 Bad Gateway

A 502 usually means your app crashed or isn't listening on the expected port.
Your app must listen on the port given in the `PORT` environment variable.
Check runtime logs under Project → Logs for a crash stack trace.

## Slow response times

- Check the region: serve users from the region closest to them.
- Starter plan instances sleep after 30 minutes of inactivity; the first request after sleep takes 5–10 seconds. Pro and Business instances never sleep.
- Enable the CDN for static assets under Project → Settings → CDN.

## Cannot log in / password reset not arriving

Password reset emails come from no-reply@cloudpeak.example — check spam.
If you signed up with GitHub OAuth, there is no password; use "Sign in with GitHub".
Accounts are locked for 15 minutes after 5 failed login attempts.

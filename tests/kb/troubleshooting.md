# Troubleshooting

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

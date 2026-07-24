# xyh-dep standalone showcase deployment

This deployment publishes the repository's public sample knowledge base at
`https://bot.xyh.wiki`. It is isolated from the existing support bot used by
`publisher.xyh.wiki/support-bot`:

- container: `rag-support-bot-showcase`
- loopback port: `127.0.0.1:8001`
- Compose project: `rag-support-bot-showcase`
- knowledge base: `/app/showcase_docs` baked into the reviewed image
- generation mode: source-only unless a dedicated showcase key is explicitly configured

The old container on `127.0.0.1:8000`, its private documents, and its environment
file are not inputs to this deployment.

## Release inputs

Build only from a clean Git commit. The immutable release name must include the
project version and full or abbreviated Git SHA, and the source archive must have
a SHA-256 checksum. The image runs as UID/GID `993:993`; do not replace it with a
root container.

Copy only these reviewed artifacts to `/data/services/rag-support-bot-showcase`:

- `compose.yaml`
- `.env`, containing the immutable image tag only
- `showcase.env`, containing public showcase settings and an empty API key by default
- the release archive and SHA-256 checksum under `releases/`

Never copy a development `.env`, workspace, private prompt, customer document,
database, or attachment directory to production.

## Deploy and rollback

Before deployment, record the current container image and copy the current
Compose/config files into a timestamped directory under `backups/`. Validate the
release checksum, load or build the exact image, then run:

```bash
docker compose --env-file .env -f compose.yaml config --quiet
docker compose --env-file .env -f compose.yaml up -d
docker inspect --format '{{.Config.User}} {{.State.Health.Status}} {{.Config.Image}}' rag-support-bot-showcase
curl -fsS http://127.0.0.1:8001/api/health
```

Rollback by restoring the previous `.env`/Compose snapshot and running the same
`docker compose ... up -d` command. The image tag must never be overwritten.

## Caddy and external verification

Append the reviewed `Caddyfile` site block to `/etc/caddy/Caddyfile`. Ensure
`/data/logs/caddy` is writable by `caddy`, validate the complete configuration,
and reload Caddy. Do not restart or edit proxy/Hysteria/Xray services.

Verify all of the following after reload:

```bash
curl -fsS https://bot.xyh.wiki/api/health
curl -fsS https://bot.xyh.wiki/robots.txt
curl -fsS https://bot.xyh.wiki/sitemap.xml
curl -fsS https://bot.xyh.wiki/ | grep -F 'RAG Support Bot Demo'
```

Also submit one same-origin chat request from the page and confirm that a
cross-origin request receives HTTP 403. Cloudflare `525` means the origin TLS
route or certificate is still invalid and is a failed deployment.

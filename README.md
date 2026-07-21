# Knowledge Base Assistant

[中文](README.zh-CN.md)

[![CI](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml)

Live demo: https://bot.xyh.wiki

![Knowledge Base Assistant preview](assets/social-preview.png)

Self-hosted document Q&A for product docs, internal manuals, policies, and
support content. It indexes local files, retrieves relevant sections, and
streams answers with citations.

Supported files: Markdown, text, PDF, Word (`.docx`), Excel (`.xlsx`), and HTML.

```html
<script
  src="https://your-domain.example/static/widget.js"
  data-api-base="https://your-domain.example">
</script>
```

## What it does

- Parses documents into section-level chunks.
- Builds an in-memory BM25 index; no vector database is required.
- Watches the document directory and reloads the index when files change.
- Streams responses over Server-Sent Events.
- Shows source citations before the answer.
- Falls back to source-only mode when no completion API key is configured.
- Exposes a floating widget that can be embedded in other websites.

## Quick Start

Python:

```bash
pip install -r requirements.txt
cp .env.example .env
export OPENAI_API_KEY=sk-...
uvicorn app:app --reload
```

Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

If `OPENAI_API_KEY` is not set, the service still works as a searchable source
viewer: it returns the most relevant excerpts and citations, but does not
synthesize an answer.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | Key for answer generation | unset |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint | official API |
| `MODEL` | Model used for generation | `gpt-5.4` |
| `TOP_K` | Chunks retrieved per question | `4` |
| `RATE_LIMIT_PER_MIN` | Per-IP chat requests per minute | `30` |
| `BOT_NAME` | Product name shown in the UI and default prompt | `Knowledge Base` |
| `BOT_TAGLINE` | Subtitle shown in the UI | sample text |
| `BOT_PLACEHOLDER` | Input placeholder text | sample text |
| `BOT_LANG` | UI language (`en`, `zh-CN`, ...) | `en` |
| `DOCS_DIR` | Knowledge-base directory | `docs/` |
| `SYSTEM_PROMPT_FILE` | Path to a custom system prompt | built-in prompt |
| `SHOW_KB_PANEL` | Show loaded documents in the UI | `false` |
| `SHOW_SOURCES` | Send and display document source labels and ask the model for citations | `true` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | same-origin only |

## Embed the Widget

```html
<script
  src="https://your-domain.example/static/widget.js"
  data-api-base="https://your-domain.example">
</script>
```

Use `data-open="true"` to open the panel on page load.

For a different website origin, set:

```bash
export ALLOWED_ORIGINS=https://your-site.com
```

### Content Security Policy (CSP)

The widget renders its isolated UI in a Shadow DOM and loads `widget.css` as a
separate asset. If the bot is exposed through a same-origin reverse proxy such
as `/support-bot/`, a minimal policy is:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; connect-src 'self'; style-src 'self'
```

For a cross-origin deployment, allow the bot origin in `script-src`,
`connect-src`, and `style-src`, then configure `ALLOWED_ORIGINS` on the bot:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://bot.example.com; connect-src 'self' https://bot.example.com; style-src 'self' https://bot.example.com
```

Keep all directives restricted to trusted origins. The widget does not require
`'unsafe-inline'` for scripts or styles.

If the launcher is missing from the bottom-right corner, check the browser
console for CSP or CORS violations, confirm that `widget.js`, `widget.css`, and
`/api/config` return HTTP 200, and hard-refresh the host page after deployment.

See `examples/embed.html` for a minimal host page.

## HTTP API

`POST /api/chat`

```json
{
  "message": "How do I reset my password?",
  "history": []
}
```

The response is an SSE stream:

- `sources`: list of source labels when `SHOW_SOURCES=true`
- `token`: streamed answer text
- `done`: end of stream

Other endpoints:

- `GET /api/config`
- `GET /api/health`
- `GET /api/kb` when `SHOW_KB_PANEL=true`

See `examples/curl-sse.sh` for a command-line SSE example.

## Use Cases

- Customer support knowledge bases
- Internal documentation search
- Policy and compliance Q&A
- PDF, Word, and Excel document search
- Website chat widgets for existing docs

More notes: `docs-public/use-cases.md`.

## How It Works

1. `rag/ingest.py` loads files and splits them by document structure:
   headings for Markdown/HTML/Word, pages for PDF, sheets and rows for Excel.
2. `rag/retriever.py` tokenizes chunks and builds a BM25 index. CJK text is
   indexed with character bigrams.
3. `rag/index.py` fingerprints the document directory and rebuilds the index in
   the background when files change.
4. `app.py` retrieves the top matching chunks for each question, adds them to
   the prompt, and streams the generated answer.
5. `static/widget.js` and `static/widget.css` render the floating browser widget
   and consume the SSE stream.

For larger corpora, the retriever can be replaced with a vector search backend
without changing the ingestion or HTTP layers.

## Production Updates

Keep the source checkout, runtime deployment, and knowledge-base documents in
separate directories. For each release:

1. Pull the reviewed source revision and install dependencies in the service's
   virtual environment.
2. Synchronize application and static assets, including both `widget.js` and
   `widget.css`.
3. Restart the service, then verify `/api/health`, `/api/config`, the two widget
   assets, and one real chat request through the public reverse proxy.
4. Hard-refresh the host site so cached widget assets cannot hide a bad rollout.

Treat the configured `DOCS_DIR` as the canonical knowledge base. Add or replace
documents there instead of editing generated index data. The service detects
document fingerprints and rebuilds the in-memory index automatically; verify a
changed fact with a real question after every documentation update. Keep
product-version details in the documents themselves and update or remove stale
pages during each product release.

## Development

```bash
python3 -m pytest tests/ -q
node --check static/widget.js
python3 -m pytest tests/test_widget_assets.py -q
```

Docker files are included for deployment:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

## License

MIT

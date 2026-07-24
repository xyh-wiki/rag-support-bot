# Changelog

## Unreleased

- Pin production dependencies and run the container as a non-root user with a
  health check and reduced privileges.
- Add an isolated `xyh-dep` deployment profile for `bot.xyh.wiki`.
- Publish accurate project metadata, remove unsupported demo metrics, and add a
  public XML sitemap.

## v0.1.0

Initial public release.

- Document ingestion for Markdown, text, PDF, Word, Excel, and HTML
- BM25 retrieval with CJK tokenization
- Hot-reloaded document index
- Citation-first SSE response stream
- Source-only mode without an API key
- Floating website widget with Shadow DOM style isolation
- Optional knowledge-base panel for staging and demos
- Docker and docker-compose examples

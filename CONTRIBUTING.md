# Contributing

Issues and pull requests are welcome. Keep changes small and easy to review.

## Local Checks

```bash
python3 -m pytest tests/ -q
node --check static/widget.js
```

## Pull Requests

- Describe the behavior change, not only the files changed.
- Add or update tests for parser, retrieval, or API behavior.
- Avoid committing private documents, API keys, logs, or generated cache files.
- Keep UI changes self-contained in `static/widget.js` unless the API contract changes.

## Document Parsers

New document formats should be implemented in `rag/ingest.py` and covered by a
small fixture under `tests/fixtures/`.

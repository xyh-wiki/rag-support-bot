# v0.1.0 - Initial public release

This release contains the first public version of Knowledge Base Assistant.

Highlights:

- Ingest Markdown, text, PDF, Word, Excel, and HTML files
- Retrieve source sections with BM25 and CJK tokenization
- Stream answers over SSE with citations
- Run in source-only mode without an API key
- Embed the floating chat widget on external websites
- Run locally with Python or Docker Compose

Suggested quick check after deployment:

```bash
curl -N -H 'Content-Type: application/json' \
  -d '{"message":"What are the API rate limits?","history":[]}' \
  http://localhost:8000/api/chat
```

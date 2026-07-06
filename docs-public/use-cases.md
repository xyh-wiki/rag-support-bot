# Use Cases

This project is a fit when the source material already exists as files and the
main requirement is to answer questions with traceable citations.

## Customer support knowledge base

Index product docs, troubleshooting guides, billing policies, and release notes.
Embed the widget on a help center or in an internal support console.

## Internal documentation search

Index onboarding docs, engineering runbooks, HR policies, and operations notes.
Keep the deployment inside a private network and use source-only mode if answer
generation is not required.

## Policy and compliance Q&A

Index policy manuals, audit checklists, and procedure documents. Keep citations
visible so reviewers can jump back to the source section.

## PDF, Word, and Excel search

Use the parsers for mixed document libraries. Word files are split by heading,
PDF files by page, and Excel files by worksheet and row.

## Website chat widget

Serve the backend from one domain and embed `static/widget.js` in another site.
Set `ALLOWED_ORIGINS` for browser-based cross-origin calls.

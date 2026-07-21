# Security

Do not open public issues for secrets or vulnerabilities.

For sensitive reports, email the repository owner or open a private advisory if
available.

## Deployment Notes

- Keep `.env`, private prompts, and customer documents out of git.
- Set `SHOW_KB_PANEL=false` for public deployments unless the document list is
  intended to be visible.
- The chat endpoint is restricted to the service's own showcase origin. Do not
  add cross-origin access or publish it as an integration API.
- Rotate API keys if they appear in logs, screenshots, or issue reports.

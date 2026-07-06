# Security

Do not open public issues for secrets or vulnerabilities.

For sensitive reports, email the repository owner or open a private advisory if
available.

## Deployment Notes

- Keep `.env`, private prompts, and customer documents out of git.
- Set `SHOW_KB_PANEL=false` for public deployments unless the document list is
  intended to be visible.
- Restrict `ALLOWED_ORIGINS` to trusted origins when embedding the widget on
  external websites.
- Rotate API keys if they appear in logs, screenshots, or issue reports.

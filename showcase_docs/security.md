# Security and Compliance

## Single sign-on

Business workspaces support SAML 2.0 single sign-on. Supported identity providers include Okta, Microsoft Entra ID, Google Workspace, and OneLogin.

To configure SSO, upload identity provider metadata, set the service provider ACS URL in the identity provider, and test login with a non-owner account before enforcing SSO.

## Audit logs

Audit logs record sign-ins, failed sign-ins, document imports, document deletions, role changes, token creation, token deletion, billing changes, and workspace exports.

Business workspaces retain audit logs for 365 days. Logs can be exported as CSV from Settings -> Security -> Audit logs.

## Data retention

Deleted documents remain recoverable for 30 days. After 30 days, document content and search index entries are permanently removed. Backups are retained for 35 days and encrypted at rest.

## API token safety

API tokens are shown only once at creation time. Store them in a secret manager. If a token appears in a browser console, issue tracker, screenshot, or log file, revoke it immediately and create a new token.

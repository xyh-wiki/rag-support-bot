# Getting Started

## Creating your first project

1. Sign up at cloudpeak.example and verify your email.
2. Click **New Project** in the dashboard.
3. Choose a region (us-east, eu-west, or ap-southeast).
4. Connect your GitHub repository or push code with the CloudPeak CLI.

Your first deployment starts automatically after the repository is connected.

## Installing the CLI

```
npm install -g @cloudpeak/cli
cloudpeak login
```

The CLI requires Node.js 18 or later. Run `cloudpeak deploy` from your project root to deploy manually.

## Custom domains

Add a custom domain under Project → Settings → Domains. Point a CNAME record at `edge.cloudpeak.example`. SSL certificates are issued automatically via Let's Encrypt within a few minutes of DNS propagation.

## Environment variables

Set environment variables under Project → Settings → Environment. Changes require a redeploy to take effect. Secrets are encrypted at rest and never shown again after saving.

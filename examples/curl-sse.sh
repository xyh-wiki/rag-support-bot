#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
QUESTION="${1:-What are the API rate limits for each plan?}"

curl -N \
  -H 'Content-Type: application/json' \
  -d "{\"message\": \"${QUESTION}\", \"history\": []}" \
  "${BASE_URL}/api/chat"

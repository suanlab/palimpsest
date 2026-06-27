#!/usr/bin/env bash
# Build the React frontend for production (same-origin serving by FastAPI).
#
# Critical gotcha: VITE_API_URL must be empty string "" for same-origin
# deployment. Setting it to "/" produces fetch calls like
#   fetch("/" + "/api/graph/...") → fetch("//api/graph/...")
# which the browser parses as a protocol-relative URL (host="api"),
# triggering ERR_NAME_NOT_RESOLVED and surfacing as "Failed to fetch"
# in the React app. Always use this script for local production builds.
#
# For GitHub Pages deployment (different origin from API), the workflow
# .github/workflows/pages.yml sets VITE_API_URL to the absolute URL
# https://scigraph.suanlab.com — that path is correct because the static
# frontend at suanlab.github.io must call a different origin.
#
# Usage:
#   scripts/build_frontend.sh                 # standard production build
#   scripts/build_frontend.sh --watch         # dev-server with live reload

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--watch" ]]; then
  cd frontend
  exec npm run dev
fi

cd frontend
# VITE_BASE=/   → serve assets from absolute root (FastAPI mount at /assets)
# VITE_API_URL=  → empty for same-origin fetches (becomes "/api/..." after
#                  the API_BASE concatenation in src/api/graphApi.ts)
VITE_BASE=/ VITE_API_URL="" npm run build

echo ""
echo "✓ Build complete. FastAPI serves dist/ at https://scigraph.suanlab.com/"
echo "  No restart required — index.html is read on every request."

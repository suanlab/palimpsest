#!/usr/bin/env bash
# SciGraph production bootstrap.
#
# One-time setup on a fresh server (Ubuntu 22.04+):
#   1. Install docker, uv, node via script
#   2. Clone the repo
#   3. Pull images via docker-compose.prod.yml
#   4. Install systemd unit
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<user>/<repo>/main/deploy/bootstrap.sh | bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/suanlab/palimpsest.git}"
TARGET_DIR="${TARGET_DIR:-/opt/palimpsest}"
SERVICE_USER="${SERVICE_USER:-suanlab}"

echo "==> Installing system dependencies"
sudo apt-get update
sudo apt-get install -y curl git build-essential ca-certificates gnupg lsb-release

echo "==> Installing Docker (if missing)"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$SERVICE_USER" || true
fi

echo "==> Installing uv"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "==> Cloning repo to $TARGET_DIR"
if [ ! -d "$TARGET_DIR/.git" ]; then
  sudo mkdir -p "$TARGET_DIR"
  sudo chown "$SERVICE_USER":"$SERVICE_USER" "$TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi
cd "$TARGET_DIR"

echo "==> Writing .env (edit NEO4J_PASSWORD before production use)"
if [ ! -f .env ]; then
  cat > .env <<'EOF'
NEO4J_AUTH=neo4j/CHANGE_ME_IN_PROD
NEO4J_PASSWORD=CHANGE_ME_IN_PROD
CORS_ORIGINS=https://suanlab.github.io
EOF
  echo "!! Edit $TARGET_DIR/.env before starting in production"
fi

echo "==> Starting stack with docker compose"
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

echo "==> Installing systemd unit (optional)"
if [ -f deploy/palimpsest-api.service ]; then
  sudo cp deploy/palimpsest-api.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now palimpsest-api 2>/dev/null || true
fi

echo "==> Done. Verify with:"
echo "    curl http://127.0.0.1:8300/api/health"
echo "    docker logs -f palimpsest-api"

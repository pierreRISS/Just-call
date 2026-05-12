#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PIDS=()

cleanup() {
  echo
  echo "Stopping dev services..."
  for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done
}

trap cleanup EXIT INT TERM

copy_env_if_missing() {
  local example_file="$1"
  local env_file="$2"

  if [[ ! -f "$env_file" && -f "$example_file" ]]; then
    cp "$example_file" "$env_file"
    echo "Created ${env_file#$ROOT_DIR/}"
  fi
}

echo "Starting PostgreSQL..."
docker compose -f "$ROOT_DIR/docker-compose.yml" up -d postgres

copy_env_if_missing "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
copy_env_if_missing "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env"

echo "Syncing backend dependencies..."
(cd "$ROOT_DIR/backend" && uv sync)

echo "Installing frontend dependencies..."
(cd "$ROOT_DIR/frontend" && npm install)

echo "Starting backend on http://localhost:8000..."
(cd "$ROOT_DIR/backend" && uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
PIDS+=("$!")

echo "Starting frontend on http://localhost:5173..."
(cd "$ROOT_DIR/frontend" && npm run dev -- --port 5173) &
PIDS+=("$!")

echo
echo "Ready:"
echo "- Frontend: http://localhost:5173"
echo "- Backend:  http://localhost:8000"
echo "- Twilio Voice URL for production: https://just-call-api.onrender.com/voice/twiml"
echo
echo "Press Ctrl+C to stop backend/frontend. PostgreSQL stays running in Docker."

wait

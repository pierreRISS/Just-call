#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WITH_NGROK=false

if [[ "${1:-}" == "--ngrok" ]]; then
  WITH_NGROK=true
fi

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
(cd "$ROOT_DIR/backend" && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
PIDS+=("$!")

echo "Starting frontend on http://localhost:5173..."
(cd "$ROOT_DIR/frontend" && npm run dev -- --port 5173) &
PIDS+=("$!")

if [[ "$WITH_NGROK" == true ]]; then
  if command -v ngrok >/dev/null 2>&1; then
    echo "Starting ngrok tunnel for backend..."
    ngrok http 8000 &
    PIDS+=("$!")
  else
    echo "ngrok is not installed. Install it, then run: ./scripts/dev.sh --ngrok"
  fi
fi

echo
echo "Ready:"
echo "- Frontend: http://localhost:5173"
echo "- Backend:  http://localhost:8000"
if [[ "$WITH_NGROK" == true ]]; then
  echo "- ngrok:    open http://127.0.0.1:4040 to copy the public HTTPS URL"
  echo "            Twilio Voice URL: https://your-ngrok-url/voice/twiml"
fi
echo
echo "Press Ctrl+C to stop backend/frontend/ngrok. PostgreSQL stays running in Docker."

wait

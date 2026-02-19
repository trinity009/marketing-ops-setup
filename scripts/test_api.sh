#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_PY="$BACKEND_DIR/.venv/bin/python"
HOST="127.0.0.1"
PORT="8000"
BASE_URL="http://${HOST}:${PORT}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "Missing virtualenv at backend/.venv. Run: make setup"
  exit 1
fi

if lsof -i TCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use. Stop the running process and retry."
  exit 1
fi

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

cd "$BACKEND_DIR"
"$VENV_PY" -m uvicorn app.main:app --host "$HOST" --port "$PORT" >/tmp/marketing_ops_api.log 2>&1 &
SERVER_PID=$!

for _ in {1..30}; do
  if curl -fsS "$BASE_URL/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "$BASE_URL/api/health" >/dev/null 2>&1; then
  echo "API failed to start. See /tmp/marketing_ops_api.log"
  exit 1
fi

echo "[1/4] Health check"
curl -fsS "$BASE_URL/api/health"
echo

echo "[2/4] Bootstrap knowledge base"
curl -fsS -X POST "$BASE_URL/api/setup/bootstrap"
echo

echo "[3/4] Run workflow"
curl -fsS -X POST "$BASE_URL/api/workflows/run" \
  -H "Content-Type: application/json" \
  -d '{"objective":"Launch a spring promo campaign","workflow_name":"standard-marketing-workflow"}'
echo

echo "[4/5] Load Maybelline baseline"
curl -fsS -X POST "$BASE_URL/api/setup/bootstrap-maybelline"
echo

echo "[5/5] List workflow runs"
curl -fsS "$BASE_URL/api/workflows"
echo

echo "API smoke test passed."

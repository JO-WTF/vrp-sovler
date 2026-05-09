#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found. Please install backend deps first: pip install fastapi uvicorn pydantic"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Please install Node.js first."
  exit 1
fi

cleanup() {
  echo "Shutting down..."
  kill "$BACK_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

uvicorn backend.main:app --host 0.0.0.0 --port 8082 --reload &
BACK_PID=$!

(
  cd frontend
  [ -d node_modules ] || npm install
  npm run dev
) &
FRONT_PID=$!

wait "$BACK_PID" "$FRONT_PID"

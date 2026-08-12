#!/usr/bin/env bash
set -e

# Load shared environment
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "ERROR: .env not found. Copy .env.example to .env and fill it."
  exit 1
fi

echo "[1/2] Starting AloneX + AI..."
python -m AloneX &
ALONEX_PID=$!

echo "[2/2] Starting WordSeek..."
cd wordseek
bun install --frozen-lockfile
bun run start &
WORDSEEK_PID=$!
cd ..

trap 'kill $ALONEX_PID $WORDSEEK_PID 2>/dev/null || true' EXIT INT TERM
wait

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${QWEN36_RAG_ENV_FILE:-$ROOT/.qwen36-rag-local.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE. Run scripts/install_qwen36_rag_local.sh first." >&2
  exit 1
fi

source "$ENV_FILE"
source "${QWEN36_RAG_VENV:?missing QWEN36_RAG_VENV}/bin/activate"

PROXY_HOST="${QWEN36_RAG_CODEX_PROXY_HOST:-127.0.0.1}"
PROXY_PORT="${QWEN36_RAG_CODEX_PROXY_PORT:-8000}"
MODEL_ALIAS="${QWEN36_RAG_CODEX_MODEL_ALIAS:-quantum-intelligence-v0.1.0}"
BACKEND_BASE_URL="http://${QWEN36_RAG_HOST:-127.0.0.1}:${QWEN36_RAG_PORT:-8011}"
BACKEND_MODEL="${QWEN36_RAG_MODEL_ALIAS:-qwen3.6-27b-rag}"

mkdir -p "$HOME/.codex"
python "$ROOT/scripts/render_codex_local_config.py" \
  --model-name "$MODEL_ALIAS" \
  --base-url "http://${PROXY_HOST}:${PROXY_PORT}/v1" \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  --workspace-root "$ROOT" \
  --trust-root "$ROOT" \
  > "$HOME/.codex/config.toml"

export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"
exec python "$ROOT/scripts/serve_qwen36_rag_codex_proxy.py" \
  --host "$PROXY_HOST" \
  --port "$PROXY_PORT" \
  --model-alias "$MODEL_ALIAS" \
  --index "${QWEN36_RAG_INDEX:?missing QWEN36_RAG_INDEX}" \
  --backend-base-url "$BACKEND_BASE_URL" \
  --backend-model "$BACKEND_MODEL" \
  --backend-api-style chat

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${QWEN36_RAG_ENV_FILE:-$ROOT/.qwen36-rag-local.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE. Run scripts/install_qwen36_rag_local.sh first." >&2
  exit 1
fi

source "$ENV_FILE"

MODEL_PATH="${QWEN36_RAG_MODEL_PATH:?missing QWEN36_RAG_MODEL_PATH}"
LLAMA_SERVER="${QWEN36_RAG_LLAMA_SERVER:-llama-server}"
HOST="${QWEN36_RAG_HOST:-127.0.0.1}"
PORT="${QWEN36_RAG_PORT:-8011}"
CTX_SIZE="${QWEN36_RAG_CTX_SIZE:-8192}"
MODEL_ALIAS="${QWEN36_RAG_MODEL_ALIAS:-qwen3.6-rag}"

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Missing model file: $MODEL_PATH" >&2
  echo "Run scripts/install_qwen36_rag_local.sh without --skip-model-download." >&2
  exit 1
fi

exec "$LLAMA_SERVER" \
  --model "$MODEL_PATH" \
  --alias "$MODEL_ALIAS" \
  --host "$HOST" \
  --port "$PORT" \
  --ctx-size "$CTX_SIZE" \
  --device none \
  --no-op-offload \
  --no-kv-offload \
  --cpu-moe \
  --reasoning off \
  --reasoning-budget 0 \
  --n-gpu-layers 0

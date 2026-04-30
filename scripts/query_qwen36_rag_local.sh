#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${QWEN36_RAG_ENV_FILE:-$ROOT/.qwen36-rag-local.env}"

if [[ $# -lt 1 ]]; then
  echo "Usage: scripts/query_qwen36_rag_local.sh 'your quantum coding question'" >&2
  exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE. Run scripts/install_qwen36_rag_local.sh first." >&2
  exit 1
fi

source "$ENV_FILE"
source "${QWEN36_RAG_VENV:?missing QWEN36_RAG_VENV}/bin/activate"

QUERY="$*"
BASE_URL="http://${QWEN36_RAG_HOST:-127.0.0.1}:${QWEN36_RAG_PORT:-8011}"
EXTRA_ARGS=()
if [[ "${QWEN36_RAG_NO_CACHE:-0}" == "1" ]]; then
  EXTRA_ARGS+=(--no-cache)
fi

python "$ROOT/scripts/query_quantum_rag.py" \
  --index "${QWEN36_RAG_INDEX:?missing QWEN36_RAG_INDEX}" \
  --query "$QUERY" \
  --base-url "$BASE_URL" \
  --api-style chat \
  --api-key dummy \
  --model "${QWEN36_RAG_MODEL_ALIAS:-qwen3.6-rag}" \
  --top-k "${QWEN36_RAG_TOP_K:-8}" \
  --max-chunks-per-source "${QWEN36_RAG_MAX_CHUNKS_PER_SOURCE:-2}" \
  --max-context-chars "${QWEN36_RAG_MAX_CONTEXT_CHARS:-1400}" \
  --max-output-tokens "${QWEN36_RAG_MAX_OUTPUT_TOKENS:-900}" \
  --timeout-seconds "${QWEN36_RAG_TIMEOUT_SECONDS:-900}" \
  "${EXTRA_ARGS[@]}"

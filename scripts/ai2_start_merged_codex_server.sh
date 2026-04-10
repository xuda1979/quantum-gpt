#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${AI2_REMOTE_ROOT:-/root/root/work/quantum-gpt}"
MODEL_ALIAS="${MODEL_ALIAS:-omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST}"
BASE_MODEL="${BASE_MODEL:-outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST/merged_full}"
LOG_PATH="${LOG_PATH:-/tmp/quantum_codex_server.log}"

cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/overlay-site-packages"
export QUANTUM_TRANSFORMERS_RUNTIME_SRC="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src"
export QUANTUM_HF_HUB_COMPAT_VERSION="1.8.0"
export QUANTUM_RUNTIME_HTTPX_STUB="0"
export PYTHONPYCACHEPREFIX="/tmp/pycache"
export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"

mkdir -p /root/.codex
python3 scripts/render_codex_local_config.py \
  --model-name "$MODEL_ALIAS" \
  --base-url "http://127.0.0.1:8000/v1" \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  >/root/.codex/config.toml

if curl --noproxy '*' -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "SERVER_ALREADY_RUNNING"
  exit 0
fi

rm -f "$LOG_PATH"
nohup python3 scripts/serve_openai_chat_adapter.py \
  --base-model "$BASE_MODEL" \
  --model-name "$MODEL_ALIAS" \
  --device cpu \
  --host 127.0.0.1 \
  --port 8000 \
  >"$LOG_PATH" 2>&1 </dev/null &

echo "CODEX_SERVER_PID:$!"

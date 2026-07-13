#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${AI2_REMOTE_ROOT:-/root/work/quantum-gpt}"
MODEL_ALIAS="${MODEL_ALIAS:-omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST}"
BASE_MODEL="${BASE_MODEL:-outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST/merged_full}"
LOG_PATH="${LOG_PATH:-/tmp/quantum_codex_server.log}"
SERVER_DEVICE="${SERVER_DEVICE:-npu}"
SERVER_MAX_NEW_TOKENS="${SERVER_MAX_NEW_TOKENS:-256}"
YUNWU_PROXY_BASE_URL="${YUNWU_PROXY_BASE_URL:-http://127.0.0.1:8011/v1}"

cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/overlay-site-packages${PYTHONPATH:+:$PYTHONPATH}"
export QUANTUM_TRANSFORMERS_RUNTIME_SRC="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src"
export QUANTUM_HF_HUB_COMPAT_VERSION="1.8.0"
export QUANTUM_RUNTIME_HTTPX_STUB="0"
export PYTHONPYCACHEPREFIX="/tmp/pycache"
export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"
export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-6}"

mkdir -p /root/.codex
python3 scripts/render_codex_local_config.py \
  --model-name "$MODEL_ALIAS" \
  --base-url "http://127.0.0.1:8000/v1" \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  --personality pragmatic \
  --workspace-root "$ROOT_DIR" \
  --trust-root "/root/work" \
  --trust-root "/" \
  --include-yunwu \
  --yunwu-base-url "$YUNWU_PROXY_BASE_URL" \
  --yunwu-env-key LOCAL_CODEX_API_KEY \
  --yunwu-claude-env-key LOCAL_CODEX_API_KEY \
  --yunwu-gemini-env-key LOCAL_CODEX_API_KEY \
  --include-huanxin-glm52-claude \
  --huanxin-glm52-env-key HUANXIN_GLM52_API_KEY \
  >/root/.codex/config.toml

if curl --noproxy '*' -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "SERVER_ALREADY_RUNNING"
  exit 0
fi

rm -f "$LOG_PATH"
nohup python3 scripts/serve_openai_chat_adapter.py \
  --base-model "$BASE_MODEL" \
  --model-name "$MODEL_ALIAS" \
  --device "$SERVER_DEVICE" \
  --max-new-tokens "$SERVER_MAX_NEW_TOKENS" \
  --host 127.0.0.1 \
  --port 8000 \
  >"$LOG_PATH" 2>&1 </dev/null &

echo "CODEX_SERVER_PID:$!"

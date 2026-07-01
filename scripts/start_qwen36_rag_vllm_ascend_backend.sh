#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_DIR="${QWEN36_HF_MODEL_DIR:-$ROOT/models/Qwen3.6-27B}"
HOST="${QWEN36_VLLM_HOST:-127.0.0.1}"
PORT="${QWEN36_VLLM_PORT:-8012}"
SERVED_MODEL="${QWEN36_VLLM_SERVED_MODEL:-qwen3.6-27b-rag}"
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
TENSOR_PARALLEL_SIZE="${QWEN36_VLLM_TENSOR_PARALLEL_SIZE:-}"
MAX_MODEL_LEN="${QWEN36_VLLM_MAX_MODEL_LEN:-8192}"
DTYPE="${QWEN36_VLLM_DTYPE:-bfloat16}"
LOG_PATH="${QWEN36_VLLM_LOG_PATH:-/tmp/qwen36_vllm_ascend_backend.log}"
PID_PATH="${QWEN36_VLLM_PID_PATH:-/tmp/qwen36_vllm_ascend_backend.pid}"

if [[ ! -f "$MODEL_DIR/config.json" ]]; then
  cat >&2 <<EOF
Missing HF/safetensors model at: $MODEL_DIR

The current GGUF file is for llama.cpp and cannot be served by vLLM Ascend.
Place the Qwen3.6-27B HF/safetensors snapshot at the path above, or set:

  QWEN36_HF_MODEL_DIR=/path/to/Qwen3.6-27B
EOF
  exit 2
fi

if [[ -z "$TENSOR_PARALLEL_SIZE" ]]; then
  TENSOR_PARALLEL_SIZE="$(python3 - <<'PY' "$VISIBLE_DEVICES"
import sys
devices = [item for item in sys.argv[1].split(",") if item.strip()]
print(max(1, len(devices)))
PY
)"
fi

export ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES"
export VLLM_PLUGINS="${VLLM_PLUGINS:-ascend}"
export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"
export NO_PROXY="${NO_PROXY:-127.0.0.1,localhost,::1}"
export no_proxy="${no_proxy:-127.0.0.1,localhost,::1}"

mkdir -p "$(dirname "$LOG_PATH")"

nohup vllm serve "$MODEL_DIR" \
  --host "$HOST" \
  --port "$PORT" \
  --served-model-name "$SERVED_MODEL" \
  --tensor-parallel-size "$TENSOR_PARALLEL_SIZE" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_MODEL_LEN" \
  --trust-remote-code \
  > "$LOG_PATH" 2>&1 &

pid=$!
printf '%s\n' "$pid" > "$PID_PATH"

echo "qwen36_vllm_ascend_backend_pid=$pid"
echo "qwen36_vllm_ascend_backend_log=$LOG_PATH"
echo "qwen36_vllm_ascend_backend_url=http://$HOST:$PORT/v1"
echo "qwen36_vllm_served_model=$SERVED_MODEL"
echo "qwen36_vllm_visible_devices=$VISIBLE_DEVICES"
echo "qwen36_vllm_tensor_parallel_size=$TENSOR_PARALLEL_SIZE"

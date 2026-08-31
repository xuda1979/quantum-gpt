#!/bin/bash
# vLLM-ascend rollout server launcher (box-side, TP=8, runs next to training).
# Usage: bash scripts/launch_vllm_rollout_server.sh [MODEL_PATH] [PORT]
MODEL="${1:-/root/work/filestorage/Qwen3.6-27B}"
PORT="${2:-8355}"
LOG="/root/work/software/quantum-gpt/outputs/vllm_server.log"
# Sleep/wake lifecycle (scripts/vllm_lifecycle.py): vLLM >= 0.10 / V1 engine
# exposes /sleep?level=N + /wake_up only with --enable-sleep-mode AND
# VLLM_SERVER_DEV_MODE=1 (dev endpoints — keep the port box-internal).
# Opt-in so the default rollout server stays minimal:
if [ "${VLLM_SLEEP_MODE:-0}" = "1" ]; then
  export VLLM_SERVER_DEV_MODE=1
  SLEEP_MODE_ARGS=(--enable-sleep-mode)
else
  SLEEP_MODE_ARGS=()
fi
cd /vllm-workspace
nohup python3 -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --port "$PORT" \
  --tensor-parallel-size 8 \
  --max-model-len 4096 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.10 \
  "${SLEEP_MODE_ARGS[@]}" \
  > "$LOG" 2>&1 < /dev/null &
echo "vllm server launching on :$PORT (pid $!) — log: $LOG"
echo "NOTE: gpu-memory-utilization 0.10 shares NPUs with training; raise when training is paused."
echo "NOTE: sleep/wake lifecycle (vllm_lifecycle.py) needs VLLM_SLEEP_MODE=1 (adds --enable-sleep-mode + VLLM_SERVER_DEV_MODE=1)."

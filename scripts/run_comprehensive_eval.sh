#!/usr/bin/env bash
# Convenience launcher for evals/subsystem/harness.py on Huanxin NPU environments.
#
# Usage:
#   ASI3 (35B, 8 NPUs, base model at /tmp/qwen35b_decompressed_for_training_asi3):
#     bash scripts/run_comprehensive_eval.sh 35b \
#         /tmp/qwen35b_decompressed_for_training_asi3 \
#         outputs/qg-35b-glm52-distill-sft-.../adapter
#
#   ASI1 (27B, 4 NPUs: 0,1,3,4):
#     ASCEND_VISIBLE_DEVICES=0,1,3,4 bash scripts/run_comprehensive_eval.sh 27b \
#         /root/work/filestorage/Qwen3.6-27B \
#         outputs/qg-27b-glm52-distill-sft-.../adapter
#
# Env vars:
#   ASCEND_VISIBLE_DEVICES  — NPU ordinals to use (default: all 8)
#   MAX_MEMORY_GIB          — per-NPU memory cap (default: 50 for 35B, 24 for 27B)
#   TASKS                   — task spec (default: standard12)
#   K                       — samples per task (default: 1)
#   MAX_NEW_TOKENS          — default: 768
#   EVAL_FILE               — held-out JSONL for CE-loss (optional)
set -euo pipefail

MODEL_SIZE="${1:-35b}"
BASE_MODEL="${2:?Usage: run_comprehensive_eval.sh <model_size> <base_model_path> <adapter_path>}"
ADAPTER_PATH="${3:?Usage: run_comprehensive_eval.sh <model_size> <base_model_path> <adapter_path>}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TASKS="${TASKS:-standard12}"
K="${K:-1}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-768}"

# default memory per NPU
if [[ "${MODEL_SIZE}" == "35b" ]]; then
    MAX_MEMORY_GIB="${MAX_MEMORY_GIB:-50}"
else
    MAX_MEMORY_GIB="${MAX_MEMORY_GIB:-24}"
fi

TS=$(date +%Y%m%dT%H%M%SZ)
ADAPTER_NAME=$(basename "$(dirname "${ADAPTER_PATH}")")
OUTPUT="${ROOT}/outputs/eval-${MODEL_SIZE}-${ADAPTER_NAME}-${TASKS}-${TS}.json"
LOG="${ROOT}/logs/eval-${MODEL_SIZE}-${ADAPTER_NAME}-${TASKS}-${TS}.log"
mkdir -p "${ROOT}/outputs" "${ROOT}/logs"

EXTRA_ARGS=""
if [[ -n "${EVAL_FILE:-}" ]]; then
    EXTRA_ARGS="${EXTRA_ARGS} --eval-file ${EVAL_FILE}"
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Launching comprehensive eval"
echo "  base_model:  ${BASE_MODEL}"
echo "  adapter:     ${ADAPTER_PATH}"
echo "  output:      ${OUTPUT}"
echo "  log:         ${LOG}"
echo "  tasks:       ${TASKS}"
echo "  k:           ${K}"
echo "  max_memory:  ${MAX_MEMORY_GIB} GiB/NPU"

nohup python3 "${ROOT}/evals/subsystem/harness.py" \
    --base-model "${BASE_MODEL}" \
    --adapter "${ADAPTER_PATH}" \
    --output "${OUTPUT}" \
    --device npu \
    --npu-max-memory-gib "${MAX_MEMORY_GIB}" \
    --max-new-tokens "${MAX_NEW_TOKENS}" \
    --k "${K}" \
    --tasks "${TASKS}" \
    ${EXTRA_ARGS} \
    > "${LOG}" 2>&1 &

PID=$!
echo "  PID: ${PID}"
echo "${PID}" > "${ROOT}/logs/eval-${MODEL_SIZE}-${ADAPTER_NAME}-${TASKS}-${TS}.pid"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Launched (nohup). Monitor with:"
echo "  tail -f ${LOG}"

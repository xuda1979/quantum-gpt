#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/work/quantum-gpt"
TRAIN_PID="${TRAIN_PID:?TRAIN_PID is required}"
TRAIN_OUT="${TRAIN_OUT:?TRAIN_OUT is required}"
BASE="/root/work/filestorage/Qwen3.8-27B"
EVAL_FILE="$ROOT/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl"
WATCH_LOG="$ROOT/logs/qg27b-sft-900x1-768-autoeval-watch.log"

cd "$ROOT"

training_is_running() {
  local state
  state="$(ps -p "$TRAIN_PID" -o stat= 2>/dev/null | tr -d '[:space:]')"
  [[ -n "$state" && "$state" != Z* ]]
}

EVAL_ROWS="$(wc -l < "$EVAL_FILE" | tr -d '[:space:]')"
if [[ "$EVAL_ROWS" != "100" ]]; then
  echo "ERROR: expected 100 eval rows, found $EVAL_ROWS" >&2
  exit 2
fi

echo "__WATCH_START__ $(date -u +%Y-%m-%dT%H:%M:%SZ)"
while [[ ! -s "$TRAIN_OUT/adapter/adapter_config.json" ]]; do
  if ! training_is_running && ! pgrep -f '[q]wen_sft_peft.py' >/dev/null; then
    echo "__TRAINING_EXITED_WITHOUT_ADAPTER__"
    exit 4
  fi
  printf '.'
  read -r -t 30 _ || true
done

echo
echo "__ADAPTER_READY__ $(date -u +%Y-%m-%dT%H:%M:%SZ)"
while training_is_running || pgrep -f '[q]wen_sft_peft.py' >/dev/null; do
  read -r -t 10 _ || true
done

echo "__TRAINING_RELEASED__ $(date -u +%Y-%m-%dT%H:%M:%SZ)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT="$ROOT/outputs/eval-qg27b-900x1-100exec-$TIMESTAMP.json"

echo "__EVAL_START__ out=$OUTPUT"
export QG_ROOT="$ROOT"
export QG_DEVICE_MAP="auto"
export QUANTUM_TRANSFORMERS_RUNTIME_SRC=""
export QWEN_SFT_ATTN_IMPL="eager"
export PYTORCH_NPU_ALLOC_CONF="max_split_size_mb:128"
export TOKENIZERS_PARALLELISM="false"
export PYTHONUNBUFFERED="1"

python3 scripts/eval_base_vs_adapter.py \
  --base "$BASE" \
  --adapter "$TRAIN_OUT/adapter" \
  --eval-file "$EVAL_FILE" \
  --out "$OUTPUT" \
  --device npu:0 \
  --max-new-tokens 768 \
  --exec-timeout 60 \
  --limit 100
RETURN_CODE=$?
echo "__EVAL_END__ rc=$RETURN_CODE out=$OUTPUT $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit "$RETURN_CODE"

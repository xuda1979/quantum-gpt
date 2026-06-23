#!/usr/bin/env bash
# Run base-vs-adapter eval on the 495 held-out samples in the ASI1 NPU env.
# Auto-selects the newest checkpoint adapter from the dedup-1k run unless ADAPTER
# is provided. Writes a JSON report to the NAS and mirrors it to S3.
set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
BASE="${BASE:-/root/work/filestorage/Qwen3.6-27B}"
EVAL_FILE="${EVAL_FILE:-data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl}"
LIMIT="${LIMIT:-0}"
MAXNEW="${MAXNEW:-768}"
DEVICE="${DEVICE:-npu:0}"

# Auto-pick newest checkpoint adapter if ADAPTER not set.
if [[ -z "${ADAPTER:-}" ]]; then
  ADAPTER="$(ls -t "$NAS_ROOT"/outputs/*/adapter/adapter_config.json 2>/dev/null | head -1 | xargs -r dirname || true)"
  if [[ -z "$ADAPTER" ]]; then
    ADAPTER="$(ls -t "$NAS_ROOT"/outputs/*/checkpoints/step-*/adapter/adapter_config.json 2>/dev/null | head -1 | xargs -r dirname || true)"
  fi
fi
[[ -n "$ADAPTER" ]] || { echo "No adapter found under $NAS_ROOT/outputs" >&2; exit 2; }
echo "__EVAL_ADAPTER__ $ADAPTER"

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/eval-base-vs-adapter-${RUN_ID}.json}"
LOG="${LOG:-$NAS_ROOT/logs/eval-base-vs-adapter-${RUN_ID}.log}"
mkdir -p "$NAS_ROOT/logs"

# Apply the NPU modeling patch (harmless if already applied) for safe forward.
python3 scripts/patch_qwen3_5_npu_modeling.py || true

echo "__EVAL_START__ base=$BASE adapter=$ADAPTER out=$OUT log=$LOG limit=$LIMIT"
nohup python3 scripts/eval_base_vs_adapter.py \
  --base "$BASE" \
  --adapter "$ADAPTER" \
  --eval-file "$EVAL_FILE" \
  --out "$OUT" \
  --device "$DEVICE" \
  --max-new-tokens "$MAXNEW" \
  --limit "$LIMIT" \
  > "$LOG" 2>&1 &
echo "$!" > /tmp/qg_eval_base_vs_adapter.pid
sleep 5
echo "__EVAL_LAUNCHED__ pid=$(cat /tmp/qg_eval_base_vs_adapter.pid) log=$LOG"
tail -n 15 "$LOG" 2>/dev/null || true

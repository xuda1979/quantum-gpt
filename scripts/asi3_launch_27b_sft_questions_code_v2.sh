#!/usr/bin/env bash
# ASI3: Qwen3.6-27B LoRA SFT on questions_and_code.jsonl (1000-row split: 900 train / 100 random eval).
# Formal training run — 1 full epoch, no max-steps cap.
# Fixes over v1:
#   - removed --max-steps 10 (smoke cap) — pass --max-steps 0 for full epoch
#   - dedup --max-trainable-parameters (only one value: 2_000_000_000)
#   - data files are pre-uploaded to ASI3 (no embedded base64)
#   - max-length 2048 -> 384 (512 reached a 64.35 GB driver-reported HBM peak on its first long batch)
#   - PYTORCH_NPU_ALLOC_CONF uses max_split_size_mb:128 only (drop expandable_segments — incompatible on NPU)
#   - chunk the 151k-vocabulary LM loss to avoid the 64.35 GB first-forward peak seen with full logits
#   - omit k_proj and LayerNorm training to preserve additional gradient/optimizer HBM reserve
#   - max-trainable-parameters 2B -> 500M (2B cap was allowing huge LoRA; 500M is plenty for r=16 on 27B)
#   - keep the 100 eval rows held out for fresh-process base-vs-adapter evaluation
#   - do not load eval data in the training process, avoiding the observed eval OOM
#   - checkpoint every 5 minutes so an interrupted run still leaves a loadable adapter
set -euo pipefail

REMOTE_ROOT="/root/work/quantum-gpt"
MODEL_PATH="/root/work/filestorage/Qwen3.8-27B"
DATA_DIR="data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
TRAIN_FILE="$REMOTE_ROOT/$DATA_DIR/train_sft_questions_code.jsonl"
EVAL_FILE="$REMOTE_ROOT/$DATA_DIR/eval_sft_questions_code.jsonl"

RUN_ID="27b-sft-formal-$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="$REMOTE_ROOT/outputs/qg-27b-sft-formal-$RUN_ID"
LOG_PATH="$REMOTE_ROOT/logs/qg-27b-sft-formal-$RUN_ID.log"
PID_FILE="$OUTPUT_DIR/asi3_27b_sft_formal.pid"

mkdir -p "$(dirname "$LOG_PATH")" "$OUTPUT_DIR"

# Verify data files / model dir exist before launching
for f in "$TRAIN_FILE" "$EVAL_FILE"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: required file missing: $f" >&2
    exit 1
  fi
done
if [[ ! -d "$MODEL_PATH" ]]; then
  echo "ERROR: model dir missing: $MODEL_PATH" >&2
  exit 1
fi

# Verify row counts (defensive: prevents silent regression if upload corrupted)
TRAIN_ROWS=$(wc -l < "$TRAIN_FILE" | tr -d '[:space:]')
EVAL_ROWS=$(wc -l < "$EVAL_FILE" | tr -d '[:space:]')
echo "[launch] train rows: $TRAIN_ROWS, eval rows: $EVAL_ROWS"
if [[ "$TRAIN_ROWS" != "900" || "$EVAL_ROWS" != "100" ]]; then
  echo "ERROR: unexpected row counts (expected 900/100)" >&2
  exit 1
fi

export PYTORCH_NPU_ALLOC_CONF="max_split_size_mb:128"
export ASCEND_LAUNCH_BLOCKING=0
export QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT=0
export QWEN_SFT_ATTN_IMPL=eager
export QWEN_SFT_CHUNKED_LOSS=1
export QWEN_SFT_LOSS_CHUNK=64
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

cd "$REMOTE_ROOT"

nohup torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
  --model-name "$MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --max-length 384 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --max-steps 0 \
  --log-steps 1 \
  --learning-rate 2e-5 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --max-trainable-parameters 500000000 \
  --checkpoint-interval-seconds 300 \
  > "$LOG_PATH" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
echo "[launch] started PID=$PID"
echo "[launch] log:      $LOG_PATH"
echo "[launch] output:   $OUTPUT_DIR"
echo "[launch] pid file: $PID_FILE"
sleep 5
ps -p "$PID" -o pid,stat,etime,cmd 2>/dev/null || echo "PROCESS_NOT_FOUND"

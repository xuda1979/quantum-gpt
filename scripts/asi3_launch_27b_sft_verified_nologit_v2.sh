#!/usr/bin/env bash
# ============================================================================
# ASI3: Qwen3.6-27B LoRA SFT — verified-only v2 dataset (no teacher logits).
#
# Dataset: data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v2
#          (917 verified rows -> 880 train / 37 eval, plain question+code, no logits)
#
# Student: Qwen3.6-27B (native bf16) with LoRA (rank 16, alpha 32).
# Trainer: training/qwen_sft_peft.py (plain cross-entropy SFT, completions-only).
# GPUs:    8 NPU (torchrun).
#
# Usage from ASI3 remote:
#   bash scripts/asi3_launch_27b_sft_verified_nologit_v2.sh launch
#   bash scripts/asi3_launch_27b_sft_verified_nologit_v2.sh status
# ============================================================================
set -euo pipefail

REMOTE_ROOT="${ASI3_REMOTE_ROOT:-/root/work/quantum-gpt}"
cd "$REMOTE_ROOT"

MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.8-27B}"
DATA_DIR="data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v2"
TRAIN_FILE="$REMOTE_ROOT/$DATA_DIR/train_chatml.jsonl"
EVAL_FILE="$REMOTE_ROOT/$DATA_DIR/eval_chatml.jsonl"

RUN_ID="${RUN_ID:-27b-sft-verified-v2-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${OUTPUT_DIR:-$REMOTE_ROOT/outputs/qg-27b-sft-verified-v2-${RUN_ID}}"
LOG_PATH="${LOG_PATH:-$REMOTE_ROOT/logs/qg-27b-sft-verified-v2-${RUN_ID}.log}"
PID_FILE="$OUTPUT_DIR/asi3_27b_sft_verified_v2.pid"

MAX_LENGTH_VAL="${MAX_LENGTH:-384}"
NUM_EPOCHS_VAL="${NUM_EPOCHS:-1}"
PER_DEVICE_BATCH_SIZE_VAL="${PER_DEVICE_BATCH_SIZE:-1}"
GRAD_ACCUM_VAL="${GRAD_ACCUM:-4}"
LEARNING_RATE_VAL="${LEARNING_RATE:-2e-5}"
LORA_RANK_VAL="${LORA_RANK:-16}"
LORA_ALPHA_VAL="${LORA_ALPHA:-32}"
LORA_DROPOUT_VAL="${LORA_DROPOUT:-0.0}"
TARGET_MODULES_VAL="${TARGET_MODULES:-q_proj v_proj o_proj gate_proj up_proj down_proj}"
MAX_STEPS_VAL="${MAX_STEPS:-0}"
CHECKPOINT_INTERVAL_SECONDS_VAL="${CHECKPOINT_INTERVAL_SECONDS:-300}"
ADAPTER_INIT="${ADAPTER_INIT:-}"

cmd="${1:-launch}"

if [[ "$cmd" == "status" ]]; then
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  echo "RUN_ID=$RUN_ID"
  echo '--- log tail ---'
  tail -n 60 "$LOG_PATH" 2>/dev/null || echo "NO_LOG"
  echo '--- adapter ---'
  ls -la "$OUTPUT_DIR/adapter" 2>/dev/null || echo "NONE"
  echo '--- checkpoints ---'
  ls -la "$OUTPUT_DIR/checkpoint-"* 2>/dev/null || echo "NONE"
  exit 0
fi

case "$OUTPUT_DIR" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUTPUT_DIR' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$(dirname "$LOG_PATH")" "$OUTPUT_DIR"

# ===== PREFLIGHT =====
echo "__PREFLIGHT_START__"

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

TRAIN_ROWS=$(wc -l < "$TRAIN_FILE" | tr -d '[:space:]')
EVAL_ROWS=$(wc -l < "$EVAL_FILE" | tr -d '[:space:]')
echo "[preflight] train rows: $TRAIN_ROWS, eval rows: $EVAL_ROWS"
if [[ "$TRAIN_ROWS" != "880" || "$EVAL_ROWS" != "37" ]]; then
  echo "ERROR: unexpected row counts (expected 880 train / 37 eval), got $TRAIN_ROWS / $EVAL_ROWS" >&2
  exit 1
fi

if [[ -n "$ADAPTER_INIT" ]]; then
  test -f "$ADAPTER_INIT/adapter_config.json" || { echo "MISSING adapter_init $ADAPTER_INIT/adapter_config.json" >&2; exit 2; }
fi

echo "__PREFLIGHT_OK__ train=$TRAIN_ROWS eval=$EVAL_ROWS out=$OUTPUT_DIR adapter_init=${ADAPTER_INIT:-none}"

# Durable run config
cat > "$OUTPUT_DIR/run_config.json" <<CFG
{
  "run_id": "qg-27b-sft-verified-v2-${RUN_ID}",
  "model": "$MODEL_PATH",
  "dataset": "$DATA_DIR (880 train / 37 eval, verified-PASS-only, no teacher_logits)",
  "teacher_model": "glm5.2",
  "strict_verify_filter": "verified_pass_ids_v2.json (917 of 1000 rows)",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "epochs": ${NUM_EPOCHS_VAL},
  "max_steps": ${MAX_STEPS_VAL},
  "lora_rank": ${LORA_RANK_VAL},
  "lora_alpha": ${LORA_ALPHA_VAL},
  "lora_dropout": ${LORA_DROPOUT_VAL},
  "target_modules": "${TARGET_MODULES_VAL}",
  "learning_rate": ${LEARNING_RATE_VAL},
  "lr_scheduler": "cosine",
  "warmup_steps": 4,
  "max_length": ${MAX_LENGTH_VAL},
  "per_device_batch_size": ${PER_DEVICE_BATCH_SIZE_VAL},
  "grad_accum": ${GRAD_ACCUM_VAL},
  "train_on_completions_only": true,
  "gradient_checkpointing": true,
  "train_layernorm": false,
  "checkpoint_interval_seconds": ${CHECKPOINT_INTERVAL_SECONDS_VAL},
  "npu_count": 8,
  "environment": "ASI3",
  "serving_note": "Use serving/run_vllm_adapter to serve the adapter; do NOT merge into base model."
}
CFG

# ===== TRAIN =====
echo "__ASI3_BEFORE_TRAIN__"

export PYTORCH_NPU_ALLOC_CONF="max_split_size_mb:128"
export ASCEND_LAUNCH_BLOCKING=0
export QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT=0
export QWEN_SFT_ATTN_IMPL=eager
export QWEN_SFT_CHUNKED_LOSS=1
export QWEN_SFT_LOSS_CHUNK=64
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

ADAPTER_ARGS=()
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
fi

cd "$REMOTE_ROOT"

nohup torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
  --model-name "$MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --device npu \
  --max-length "$MAX_LENGTH_VAL" \
  --num-epochs "$NUM_EPOCHS_VAL" \
  --max-steps "$MAX_STEPS_VAL" \
  --per-device-batch-size "$PER_DEVICE_BATCH_SIZE_VAL" \
  --gradient-accumulation-steps "$GRAD_ACCUM_VAL" \
  --learning-rate "$LEARNING_RATE_VAL" \
  --warmup-steps 4 \
  --eval-steps 20 \
  --log-steps 1 \
  --lora-rank "$LORA_RANK_VAL" \
  --lora-alpha "$LORA_ALPHA_VAL" \
  --lora-dropout "$LORA_DROPOUT_VAL" \
  --lora-backend peft \
  --target-modules $TARGET_MODULES_VAL \
  --train-on-completions-only \
  --gradient-checkpointing \
  --max-trainable-parameters 500000000 \
  --checkpoint-interval-seconds "$CHECKPOINT_INTERVAL_SECONDS_VAL" \
  "${ADAPTER_ARGS[@]}" \
  > "$LOG_PATH" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
echo "[launch] started PID=$PID"
echo "[launch] log:      $LOG_PATH"
echo "[launch] output:   $OUTPUT_DIR"
echo "[launch] pid file: $PID_FILE"
echo "__ASI3_VERIFIED_V2_SFT_27B_LAUNCHED__ pid=$PID run_id=$RUN_ID"

sleep 8
ps -p "$PID" -o pid,stat,etime,cmd 2>/dev/null || echo "PROCESS_NOT_FOUND"
echo '--- initial log tail ---'
tail -n 25 "$LOG_PATH" 2>/dev/null || true

echo ""
echo "To monitor:  tail -f $LOG_PATH"
echo "To check status:  bash scripts/asi3_launch_27b_sft_verified_nologit_v2.sh status"

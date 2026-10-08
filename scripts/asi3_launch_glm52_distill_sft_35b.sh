#!/usr/bin/env bash
# ASI3 launcher: Qwen3.6-35B-A3B LoRA SFT on the GLM5.2 soft-distillation 100-row set.
#
# Teacher: glm5.2 (top-20 logprobs preserved in source file for future soft-KL trainer).
# Student: Qwen3.6-35B-A3B (W8A8 decompressed to bf16) with LoRA (rank 16, alpha 32).
# Dataset: data/generated/glm52_soft_distill_sft_100 (90 train / 10 eval).
#
# ASI3 runs single-process sharded (world_size==1) with balanced-layers NPU map
# because the container exposes 2 NPUs and a single CPU. Output goes to the
# persistent NAS; adapter checkpoints are also mirrored to the NAS.
#
# Usage:
#   scripts/asi3_launch_glm52_distill_sft_35b.sh launch   # start training
#   scripts/asi3_launch_glm52_distill_sft_35b.sh status   # tail log + list checkpoints
#
# Optional env overrides:
#   MODEL_PATH, DATA, OUTPUT_DIR, ADAPTER_INIT, REMOTE_ROOT, NPU_MAX_MEMORY_GIB,
#   MAX_LENGTH, NUM_EPOCHS, PER_DEVICE_BATCH_SIZE, GRAD_ACCUM, LEARNING_RATE,
#   LORA_RANK, LORA_ALPHA, LORA_DROPOUT, TARGET_MODULES

set -euo pipefail

REMOTE_ROOT="${ASI3_REMOTE_ROOT:-/root/work/quantum-gpt}"
cd "$REMOTE_ROOT"
MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
DATA="${DATA:-data/generated/glm52_soft_distill_sft_iter2}"
TRAIN_FILE="$DATA/train_chatml.jsonl"
EVAL_FILE="$DATA/eval_chatml.jsonl"
RUN_ID="${RUN_ID:-glm52-distill-35b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${OUTPUT_DIR:-$REMOTE_ROOT/outputs/qg-35b-glm52-distill-sft-${RUN_ID}}"
LOG_PATH="${LOG_PATH:-$REMOTE_ROOT/logs/qg-35b-glm52-distill-sft-${RUN_ID}.log}"
DECOMPRESSED_MODEL_PATH="${DECOMPRESSED_MODEL_PATH:-/tmp/qwen35b_decompressed_for_training_asi3}"
DECOMPRESSED_DONE_MARKER="$DECOMPRESSED_MODEL_PATH/.dequant_complete"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  echo '--- log tail ---'; tail -n 60 "$LOG_PATH" 2>/dev/null || echo NO_LOG
  echo '--- adapter ---'; ls -la "$OUTPUT_DIR/adapter" 2>/dev/null || echo NONE
  exit 0
fi

# --- DURABILITY GUARDRAIL ---
case "$OUTPUT_DIR" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUTPUT_DIR' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$REMOTE_ROOT/logs" "$OUTPUT_DIR"

# ===== PREFLIGHT =====
echo "__PREFLIGHT_START__"

if [ ! -f "$TRAIN_FILE" ]; then
    TRAIN_COUNT=0
else
    TRAIN_COUNT=$(wc -l < "$TRAIN_FILE")
fi

if [ ! -f "$EVAL_FILE" ]; then
    EVAL_COUNT=0
else
    EVAL_COUNT=$(wc -l < "$EVAL_FILE")
fi

if [ "$TRAIN_COUNT" -eq 0 ] || [ "$EVAL_COUNT" -eq 0 ]; then
    echo "MISSING: train=$TRAIN_COUNT eval=$EVAL_COUNT" >&2
    exit 1
fi

ADAPTER_INIT="${ADAPTER_INIT:-}"
if [[ -n "$ADAPTER_INIT" ]]; then
  test -f "$ADAPTER_INIT/adapter_config.json" || { echo "MISSING adapter_init $ADAPTER_INIT/adapter_config.json" >&2; exit 2; }
fi

echo "__PREFLIGHT_OK__ train=$TRAIN_COUNT eval=$EVAL_COUNT out=$OUTPUT_DIR adapter_init=${ADAPTER_INIT:-none}"

# Durable record of exactly what we ran.
cat > "$OUTPUT_DIR/run_config.json" <<CFG
{
  "run_id": "qg-35b-glm52-distill-sft-${RUN_ID}",
  "model": "$MODEL_PATH",
  "decompressed_model_path": "$DECOMPRESSED_MODEL_PATH",
  "dataset": "$DATA (90 train / 10 eval, GLM5.2 teacher, soft-distillation v1)",
  "teacher_model": "glm5.2",
  "teacher_source_file": "/Users/daxu/software/data_generation/gpt55_100_en.glm52_soft_distill.jsonl",
  "teacher_source_sha256": "61a526db39bd2fd4667d6fde6bcb426d3855e5a0ada8ec58b0e440cd2acd2ed3",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "epochs": ${NUM_EPOCHS:-2},
  "lora_rank": ${LORA_RANK:-16},
  "lora_alpha": ${LORA_ALPHA:-32},
  "lora_dropout": ${LORA_DROPOUT:-0.0},
  "target_modules": "${TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}",
  "learning_rate": ${LEARNING_RATE:-2e-5},
  "lr_scheduler": "cosine",
  "warmup_steps": 4,
  "max_length": ${MAX_LENGTH:-2048},
  "per_device_batch_size": ${PER_DEVICE_BATCH_SIZE:-1},
  "grad_accum": ${GRAD_ACCUM:-4},
  "train_on_completions_only": true,
  "npu_device_map": "balanced-layers",
  "npu_max_memory_gib": ${NPU_MAX_MEMORY_GIB:-54},
  "decompression": "training/dequantize_moe_w8a8_to_bf16.py (cached at $DECOMPRESSED_MODEL_PATH)",
  "environment": "ASI3",
  "serving_note": "Use serving/run_vllm_35b_a3b_with_adapter.py to serve the adapter; do NOT merge into the W8A8 base."
}
CFG

# ===== DECOMPRESS W8A8 -> bf16 (cached) =====
echo "__DECOMPRESS_START__"
if [[ -d "$DECOMPRESSED_MODEL_PATH" && -f "$DECOMPRESSED_DONE_MARKER" ]]; then
  echo "__DECOMPRESS_CACHED__ $DECOMPRESSED_MODEL_PATH"
else
  rm -f "$DECOMPRESSED_DONE_MARKER"
  python3 training/dequantize_moe_w8a8_to_bf16.py \
    --input-dir "$MODEL_PATH" --output-dir "$DECOMPRESSED_MODEL_PATH"
  test -f "$DECOMPRESSED_DONE_MARKER" || { echo "__DECOMPRESS_FAILED__" >&2; exit 1; }
fi
echo "__DECOMPRESS_OK__ $DECOMPRESSED_MODEL_PATH"

# ===== TRAIN =====
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
# NPU fix: eager attention avoids the failing flash-attention backward op
# (aclnnFlashAttentionScoreGrad) on Ascend — matches the ASI1 27B launcher.
export QWEN_SFT_ATTN_IMPL=eager
# NPU fix: chunked cross-entropy avoids materializing the full [B,seq,vocab]
# logits tensor (OOM at loss computation for the 35B MoE vocab).
export QWEN_SFT_CHUNKED_LOSS=1
export QWEN_SFT_LOSS_CHUNK=512
# NPU fix: force non-reentrant gradient checkpointing. With balanced-layers
# device_map + low_cpu_mem_usage=True on Ascend, the default reentrant path
# raises "Function MmBackward0 returned an invalid gradient at index 1 -
# expected device meta but got npu:0" because SavedVariable tensors bypass
# accelerate's meta->npu dispatch hooks. See qwen_sft_peft.py for details.
export QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT=0
export PYTHONUNBUFFERED=1

MAX_LENGTH_VAL="${MAX_LENGTH:-2048}"
NUM_EPOCHS_VAL="${NUM_EPOCHS:-2}"
PER_DEVICE_BATCH_SIZE_VAL="${PER_DEVICE_BATCH_SIZE:-1}"
GRAD_ACCUM_VAL="${GRAD_ACCUM:-4}"
LEARNING_RATE_VAL="${LEARNING_RATE:-2e-5}"
LORA_RANK_VAL="${LORA_RANK:-16}"
LORA_ALPHA_VAL="${LORA_ALPHA:-32}"
LORA_DROPOUT_VAL="${LORA_DROPOUT:-0.0}"
TARGET_MODULES_VAL="${TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
NPU_MAX_MEMORY_GIB_VAL="${NPU_MAX_MEMORY_GIB:-54}"

ADAPTER_ARGS=()
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
fi

echo "__ASI3_BEFORE_TRAIN__"
nohup python3 training/qwen_sft_peft.py \
  --model-name "$DECOMPRESSED_MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map "${ASI3_NPU_DEVICE_MAP:-balanced-layers}" \
  --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB_VAL" \
  --npu-cpu-offload-fraction "${ASI3_NPU_CPU_OFFLOAD_FRACTION:-0.0}" \
  --max-length "$MAX_LENGTH_VAL" \
  --num-epochs "$NUM_EPOCHS_VAL" \
  --max-steps -1 \
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
  --freeze-param-regex '.*\.(mlp\.gate|router)\..*' \
  --train-on-completions-only \
  $([[ "${ASI3_NO_GRADIENT_CHECKPOINTING:-0}" != "1" ]] && echo "--gradient-checkpointing") \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000 \
  --checkpoint-interval-seconds 900 \
  "${ADAPTER_ARGS[@]}" \
  > "$LOG_PATH" 2>&1 &
PID=$!
echo "$PID" > "$OUTPUT_DIR/asi3_glm52_distill.pid"
echo "__ASI3_GLM52_DISTILL_LAUNCHED__ pid=$PID log=$LOG_PATH out=$OUTPUT_DIR"
sleep 8
ps -p "$PID" -o pid,stat,etime,cmd 2>/dev/null || echo "PROCESS_NOT_FOUND"
echo '--- initial log tail ---'; tail -n 25 "$LOG_PATH" 2>/dev/null || true

echo ""
echo "To monitor: tail -f $LOG_PATH"
echo "To check status: scripts/asi3_launch_glm52_distill_sft_35b.sh status"

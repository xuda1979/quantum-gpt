#!/usr/bin/env bash
# ASI2 launcher: Qwen3.6-35B-A3B LoRA SFT on the GLM5.2 soft-distillation 100-row set.
#
# Teacher: glm5.2 (top-20 logprobs preserved in source file for future soft-KL trainer).
# Student: Qwen3.6-35B-A3B (W8A8 decompressed to bf16) with LoRA (rank 16, alpha 32).
# Dataset: data/generated/glm52_soft_distill_sft_100 (90 train / 10 eval).
#
# DURABILITY: output-dir MUST be on the persistent NAS (/root/work). The script
# refuses to launch if the output dir is under ephemeral /workspace. Logs and
# run_config also go to NAS. Periodic adapter checkpoints to NAS + S3 mirror.
#
# Usage:
#   scripts/asi2_launch_glm52_distill_sft_35b.sh launch   # start training
#   scripts/asi2_launch_glm52_distill_sft_35b.sh status   # tail log + list checkpoints
#
# Optional env overrides:
#   MODEL_PATH, DATA, OUTPUT_DIR, ADAPTER_INIT, NAS_ROOT, NPROC, MASTER_PORT,
#   RCLONE_CONF, INER_S3_BUCKET

set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
DATA="${DATA:-data/generated/glm52_soft_distill_sft_100}"
RUN_ID="${RUN_ID:-glm52-distill-35b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${OUTPUT_DIR:-$NAS_ROOT/outputs/qg-35b-glm52-distill-sft-${RUN_ID}}"
LOG="${LOG:-$NAS_ROOT/logs/qg-35b-glm52-distill-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_35b_glm52_distill_sft.pid}"
MASTER_PORT="${MASTER_PORT:-29635}"
NPROC="${NPROC:-8}"
ADAPTER_INIT="${ADAPTER_INIT:-}"

TRAIN_FILE="$DATA/train_chatml.jsonl"
EVAL_FILE="$DATA/eval_chatml.jsonl"
DECOMPRESSED_MODEL_PATH="/tmp/qwen35b_decompressed_for_training"
DECOMPRESSED_DONE_MARKER="$DECOMPRESSED_MODEL_PATH/.dequant_complete"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUTPUT_DIR/checkpoints" 2>/dev/null || echo NONE
  echo '--- adapter ---'; ls -la "$OUTPUT_DIR/adapter" 2>/dev/null || echo NONE
  exit 0
fi

# --- DURABILITY GUARDRAIL ---
case "$OUTPUT_DIR" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUTPUT_DIR' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$NAS_ROOT/logs" "$OUTPUT_DIR"

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

if [[ -n "$ADAPTER_INIT" ]]; then
  test -f "$ADAPTER_INIT/adapter_config.json" || { echo "MISSING adapter_init $ADAPTER_INIT/adapter_config.json" >&2; exit 2; }
fi

echo "__PREFLIGHT_OK__ train=$TRAIN_COUNT eval=$EVAL_COUNT out=$OUTPUT_DIR adapter_init=${ADAPTER_INIT:-none}"

# Durable record of exactly what we ran.
cat > "$OUTPUT_DIR/run_config.json" <<CFG
{
  "run_id": "qg-35b-glm52-distill-sft-${RUN_ID}",
  "model": "$MODEL_PATH",
  "decompressed_to": "$DECOMPRESSED_MODEL_PATH",
  "dataset": "$DATA (90 train / 10 eval, GLM5.2 teacher, soft-distillation v1)",
  "teacher_model": "glm5.2",
  "teacher_source_file": "/Users/daxu/software/data_generation/gpt55_100_en.glm52_soft_distill.jsonl",
  "teacher_source_sha256": "61a526db39bd2fd4667d6fde6bcb426d3855e5a0ada8ec58b0e440cd2acd2ed3",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "epochs": 2,
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.0,
  "target_modules": "q_proj k_proj v_proj o_proj gate_proj up_proj down_proj",
  "learning_rate": 2e-5,
  "max_length": 2048,
  "per_device_batch_size": 1,
  "grad_accum": 4,
  "train_on_completions_only": true,
  "train_layernorm": true,
  "checkpoint_interval_seconds": 900,
  "visible_devices": "single-process python3, npu_device_map=balanced-layers (all 8 NPUs, world_size=1)",
  "output_dir": "$OUTPUT_DIR",
  "distillation_mode": "hard_sft_on_teacher_completion",
  "soft_distill_logprobs_preserved": true,
  "soft_distill_logprobs_location": "source file distillation.logprob_positions[*].top_logprobs (top-20)"
}
CFG

# ===== INSTALL DEPS =====
echo "__DEPS_CHECK__"
pip3 install -q peft 2>/dev/null || pip3 install peft
pip3 install -q accelerate 2>/dev/null || pip3 install accelerate
pip3 install -q huggingface_hub 2>/dev/null || pip3 install huggingface_hub
pip3 install -q compressed-tensors 2>/dev/null || pip3 install compressed-tensors
echo "__DEPS_OK__ peft accelerate hub compressed-tensors"

# ===== DECOMPRESS MODEL =====
echo "__DECOMPRESS_START__"

if [ -d "$DECOMPRESSED_MODEL_PATH" ] && [ -f "$DECOMPRESSED_DONE_MARKER" ]; then
    echo "__DECOMPRESS_CACHED__ $DECOMPRESSED_MODEL_PATH (complete cached model found)"
else
    echo "Decompressing 35B MoE expert int8 tensors to bf16 (this can take a while)..."
    rm -f "$DECOMPRESSED_DONE_MARKER"
    python3 training/dequantize_moe_w8a8_to_bf16.py \
      --input-dir "$MODEL_PATH" \
      --output-dir "$DECOMPRESSED_MODEL_PATH"
    DECOMP_STATUS=$?
    if [ "$DECOMP_STATUS" -ne 0 ]; then
        echo "__DECOMPRESS_FAILED__"
        exit 1
    fi
    if [ ! -f "$DECOMPRESSED_DONE_MARKER" ]; then
        echo "__DECOMPRESS_FAILED__ missing completion marker"
        exit 1
    fi
fi

echo "__DECOMPRESS_OK__ $DECOMPRESSED_MODEL_PATH"

# ===== LAUNCH TRAINING =====
echo "__ASI2_GLM52_DISTILL_LAUNCH_START__"

# Use the decompressed model for training
ACTUAL_MODEL_PATH="$DECOMPRESSED_MODEL_PATH"

# NPU OOM guards: eager attention + chunked cross-entropy.
export QWEN_SFT_ATTN_IMPL=eager
export QWEN_SFT_CHUNKED_LOSS=1
export QWEN_SFT_LOSS_CHUNK=512
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

ADAPTER_ARGS=()
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
fi

# 35B bf16 (~70GB) does NOT fit on a single 60GB NPU under DDP (each rank
# would load the full model). Use single-process sharded loading with the
# balanced-layers NPU device map instead, matching ASI3.
NPU_MAX_MEMORY_GIB_VAL="${NPU_MAX_MEMORY_GIB:-54}"

nohup python3 training/qwen_sft_peft.py \
  --model-name "$ACTUAL_MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB_VAL" \
  --max-length 2048 \
  --num-epochs 2 \
  --max-steps -1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --warmup-steps 4 \
  --eval-steps 20 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --lora-backend peft \
  --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --freeze-param-regex '.*\.(mlp\.gate|router)\..*' \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000 \
  --checkpoint-interval-seconds 900 \
  "${ADAPTER_ARGS[@]}" \
  > "$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"

echo "__ASI2_GLM52_DISTILL_LAUNCHED__ pid=$PID log=$LOG out=$OUTPUT_DIR"
sleep 8
ps -p "$PID" -o pid,stat,etime,cmd 2>/dev/null || true
echo '--- initial log tail ---'; tail -n 25 "$LOG" 2>/dev/null || true

# --- DURABILITY: off-box mirror of outputs to INER S3 every 5 min ---
RCLONE_CONF="${RCLONE_CONF:-/tmp/iner-rclone.conf}"
S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
if [[ -f "$RCLONE_CONF" ]] && ! grep -q '__INER_SECRET__' "$RCLONE_CONF" 2>/dev/null; then
  RCLONE_BIN="$(command -v rclone || true)"
  if [[ -n "$RCLONE_BIN" ]]; then
    S3_DEST="iner:${S3_BUCKET}/software/quantum-gpt/outputs/$(basename "$OUTPUT_DIR")"
    MIRROR_PID_FILE="/tmp/qg_35b_glm52_distill_mirror.pid"
    nohup bash -c '
      TRAIN_PID="'"$(cat "$PIDFILE")"'"
      while kill -0 "$TRAIN_PID" 2>/dev/null; do
        "'"$RCLONE_BIN"'" --config "'"$RCLONE_CONF"'" copy "'"$OUTPUT_DIR"'" "'"$S3_DEST"'" \
          --s3-force-path-style --transfers 4 --checkers 4 >/dev/null 2>&1 || true
        sleep 300
      done
      "'"$RCLONE_BIN"'" --config "'"$RCLONE_CONF"'" copy "'"$OUTPUT_DIR"'" "'"$S3_DEST"'" \
        --s3-force-path-style --transfers 4 --checkers 4 >/dev/null 2>&1 || true
    ' > /tmp/qg_35b_glm52_distill_mirror.log 2>&1 &
    echo "$!" > "$MIRROR_PID_FILE"
    echo "__S3_MIRROR_STARTED__ pid=$(cat "$MIRROR_PID_FILE") dest=$S3_DEST (every 300s + final)"
  else
    echo "__S3_MIRROR_SKIPPED__ rclone not found; relying on NAS persistence only"
  fi
else
  echo "__S3_MIRROR_SKIPPED__ no usable $RCLONE_CONF; relying on NAS persistence only"
fi

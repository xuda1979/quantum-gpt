#!/bin/bash
#
# ASI2 one-shot launcher: Qwen3.6-35B-A3B LoRA SFT on the dedup-1k dataset.
#
# Durable by design:
#   - Decompresses W8A8 -> bf16 to NAS (cached via .dequant_complete)
#   - Writes ALL outputs/checkpoints/logs to NAS (/root/work/filestorage), never /vllm-workspace
#   - Runs nohup'd + disowned so it survives shell/session disconnect
#   - Hourly time-based LoRA checkpoints to <out>/checkpoints/step-<N>/adapter
#
# LoRA spec (per user): 1 epoch, NO k_proj, router/gate frozen, best-practice settings.
#
set -euo pipefail

# ---- Locations (NAS = durable) -------------------------------------------------
ROOT="${ROOT:-/root/work/filestorage}"
REPO="${REPO:-/root/work/quantum-gpt}"
MODEL_PATH="${MODEL_PATH:-$ROOT/Qwen3.6-35B-A3B-W8A8}"
DECOMP="${DECOMP:-$ROOT/qwen35b_decompressed_for_training}"
DECOMP_MARKER="$DECOMP/.dequant_complete"

DATA_DIR="${DATA_DIR:-$REPO/data/generated/quantum_finetune_verified_chat_sft_dedup_1k}"
TRAIN_FILE="${TRAIN_FILE:-$DATA_DIR/train_chatml.jsonl}"
EVAL_FILE="${EVAL_FILE:-$DATA_DIR/eval_chatml.jsonl}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT:-$ROOT/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-$STAMP}"
LOGDIR="$REPO/logs"
mkdir -p "$LOGDIR" "$(dirname "$OUT")"
TRAIN_LOG="$OUT/train.log"

cd "$REPO"

# ---- Preflight ----------------------------------------------------------------
echo "__PREFLIGHT__"
[ -f "$TRAIN_FILE" ] || { echo "MISSING train: $TRAIN_FILE"; exit 1; }
[ -f "$EVAL_FILE" ]  || { echo "MISSING eval:  $EVAL_FILE";  exit 1; }
TRAIN_N=$(wc -l < "$TRAIN_FILE"); EVAL_N=$(wc -l < "$EVAL_FILE")
echo "train=$TRAIN_N eval=$EVAL_N model=$MODEL_PATH out=$OUT"
[ "$TRAIN_N" -gt 0 ] && [ "$EVAL_N" -gt 0 ] || { echo "empty dataset"; exit 1; }

# ---- Deps ---------------------------------------------------------------------
echo "__DEPS__"
pip3 install -q peft accelerate huggingface_hub compressed-tensors 2>/dev/null || \
  pip3 install peft accelerate huggingface_hub compressed-tensors

# ---- Decompress W8A8 -> bf16 (cached) -----------------------------------------
echo "__DECOMPRESS__"
if [ -d "$DECOMP" ] && [ -f "$DECOMP_MARKER" ]; then
  echo "cached: $DECOMP"
else
  rm -f "$DECOMP_MARKER"
  python3 training/dequantize_moe_w8a8_to_bf16.py --input-dir "$MODEL_PATH" --output-dir "$DECOMP"
  [ -f "$DECOMP_MARKER" ] || { echo "decompress failed (no marker)"; exit 1; }
fi
echo "decompressed: $DECOMP"

# ---- Launch (durable, background) ---------------------------------------------
echo "__LAUNCH__ out=$OUT"
mkdir -p "$OUT"

# Static padding to a fixed length keeps tensor shapes constant so the Ascend
# TBE compiler compiles kernels once instead of recompiling per sequence length
# (critical on low-core NPU hosts). Persist the kernel cache to NAS so compiled
# kernels survive pod reclaim and are never recompiled.
export QWEN_SFT_PAD_TO_MAX_LENGTH="${QWEN_SFT_PAD_TO_MAX_LENGTH:-1}"
export QWEN_SFT_ATTN_IMPL="${QWEN_SFT_ATTN_IMPL:-eager}"
export ASCEND_CACHE_PATH="${ASCEND_CACHE_PATH:-$ROOT/ascend_kernel_cache}"
mkdir -p "$ASCEND_CACHE_PATH"

# Gradient checkpointing recomputes the full forward during backward. On this
# host the MoE router top-k (ArgSort) falls back to AiCpu, and with only 1 CPU
# core that recompute stalls the backward pass. Default OFF here; there is ample
# NPU memory (35B bf16 + tiny LoRA, bs1/seq512 across 8x54GiB) to hold full
# activations. Set GRADIENT_CHECKPOINTING=1 to re-enable.
GRADIENT_CHECKPOINTING="${GRADIENT_CHECKPOINTING:-0}"
GC_FLAG=""
if [ "$GRADIENT_CHECKPOINTING" = "1" ]; then GC_FLAG="--gradient-checkpointing"; fi
echo "pad_to_max_length=$QWEN_SFT_PAD_TO_MAX_LENGTH attn=$QWEN_SFT_ATTN_IMPL gradient_checkpointing=$GRADIENT_CHECKPOINTING ascend_cache=$ASCEND_CACHE_PATH"

nohup python3 training/qwen_sft_peft.py \
  --model-name "$DECOMP" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length 512 \
  --num-epochs 1 \
  --max-steps 250 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 1e-4 \
  --warmup-steps 8 \
  --eval-steps 50 \
  --log-steps 1 \
  --checkpoint-interval-seconds 3600 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --freeze-param-regex '.*\.(mlp\.gate|router)\..*' \
  --train-on-completions-only \
  $GC_FLAG \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000 \
  > "$TRAIN_LOG" 2>&1 &

PID=$!
echo "$PID" > "$LOGDIR/asi2_dedup1k.pid"
disown "$PID" 2>/dev/null || true
echo "__LAUNCHED__ pid=$PID log=$TRAIN_LOG"
echo "Tail with:  tail -f $TRAIN_LOG"

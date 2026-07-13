#!/bin/bash
#
# ASI2 launcher: Train Qwen3.6-35B-A3B-W8A8 on Ascend by decompressing to full precision.
#
# Problem: 35B-W8A8 has int8-quantized MoE experts. Ascend aclnnMm rejects int8 matmuls.
# Solution: Decompress to bf16 before training (run this launcher).
#

set -e

MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
TRAIN_FILE="${TRAIN_FILE:-data/generated/quantum_finetune_verified_chat_sft/train_chatml.jsonl}"
EVAL_FILE="${EVAL_FILE:-data/generated/quantum_finetune_verified_chat_sft/eval_chatml.jsonl}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/qwen36-35b-w8a8-verified10k-sft-20260617}"
DECOMPRESSED_MODEL_PATH="/tmp/qwen35b_decompressed_for_training"
DECOMPRESSED_DONE_MARKER="$DECOMPRESSED_MODEL_PATH/.dequant_complete"

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
    echo "MISSING: train=$TRAIN_COUNT eval=$EVAL_COUNT"
    exit 1
fi

echo "__PREFLIGHT_OK__ train=$TRAIN_COUNT eval=$EVAL_COUNT"

# ===== INSTALL DEPS =====
echo "__DEPS_CHECK__"

pip3 install -q peft 2>/dev/null || pip3 install peft
pip3 install -q accelerate 2>/dev/null || pip3 install accelerate
pip3 install -q huggingface_hub 2>/dev/null || pip3 install huggingface_hub
pip3 install -q compressed-tensors 2>/dev/null || pip3 install compressed-tensors

echo "__DEPS_OK__ peft accelerate hub"

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
echo "__ASI2_LAUNCH_START__"

# Use the decompressed model for training
ACTUAL_MODEL_PATH="$DECOMPRESSED_MODEL_PATH"

python3 training/qwen_sft_peft.py \
  --model-name "$ACTUAL_MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length 512 \
  --max-steps 2500 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --eval-steps 50 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000

PID=$!
echo "PID=$PID"
echo "$PID" > /tmp/asi2_qwen35b_sft.pid

echo "__ASI2_LAUNCHED__ pid=$PID"

wait "$PID"
EXIT_CODE=$?

echo "__ASI2_TRAINING_COMPLETE__ exit_code=$EXIT_CODE"
exit "$EXIT_CODE"

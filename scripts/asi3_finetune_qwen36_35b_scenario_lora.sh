#!/usr/bin/env bash
# =============================================================================
# ASI3 (Huanxin) launcher: LoRA finetune Qwen3.6-35B-A3B on the scenario-modeling
# code dataset (场景建模代码数据) for ONE epoch.
#
# RUN THIS INSIDE THE ASI3 TRAIN-DEV CONTAINER.
#
# The 35B-A3B base ships as W8A8 (int8 MoE experts). Ascend aclnnMm rejects int8
# matmul, so we first DECOMPRESS the experts to bf16 (training/dequantize_moe_
# w8a8_to_bf16.py), then LoRA-train on top of the frozen bf16 base. Because a 35B
# model does not fit per-NPU for DDP, we shard the model across the visible NPUs
# in a single process (--npu-device-map balanced-layers).
#
# LoRA budget chosen for a SMALL (~102 examples) 1-epoch run on a 35B-A3B MoE:
#   rank 16 / alpha 32 (alpha = 2*rank), dropout 0.05, LR 1e-4.
#   Targets: attention q/k/v/o + expert MLP gate/up/down. The MoE router/gate
#   network is intentionally NOT targeted (the suffix list never matches it),
#   so expert routing / load-balancing stays stable.
# =============================================================================
set -euo pipefail

REMOTE_ROOT="${ASI3_REMOTE_ROOT:-/root/work/quantum-gpt}"
MODEL_NAME="${ASI3_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
DECOMPRESSED_MODEL_PATH="${ASI3_DECOMPRESSED_MODEL_PATH:-/tmp/qwen35b_decompressed_for_training}"
DECOMPRESSED_DONE_MARKER="$DECOMPRESSED_MODEL_PATH/.dequant_complete"

TRAIN_FILE="${ASI3_TRAIN_FILE:-data/generated/scenario-modeling-md-v1/train.jsonl}"
OUTPUT_DIR="${ASI3_OUTPUT_DIR:-outputs/qwen36-35b-scenario-modeling-lora-r16-1ep}"
LOG_PATH="${ASI3_LOG_PATH:-logs/asi3_qwen36_35b_scenario_lora.log}"

# Visible NPUs are fixed by the container allocation. Use ALL of them.
# (Override ASCEND_RT_VISIBLE_DEVICES to pin a subset.)
NPU_MAX_MEMORY_GIB="${ASI3_NPU_MAX_MEMORY_GIB:-54}"

# ---- 1-epoch hyper-parameters -----------------------------------------------
MAX_LENGTH="${ASI3_MAX_LENGTH:-3072}"
NUM_EPOCHS="${ASI3_NUM_EPOCHS:-1}"
PER_DEVICE_BATCH_SIZE="${ASI3_PER_DEVICE_BATCH_SIZE:-1}"
GRAD_ACCUM="${ASI3_GRAD_ACCUM:-8}"
LEARNING_RATE="${ASI3_LEARNING_RATE:-1e-4}"
LOG_STEPS="${ASI3_LOG_STEPS:-1}"
LORA_RANK="${ASI3_LORA_RANK:-16}"
LORA_ALPHA="${ASI3_LORA_ALPHA:-32}"
LORA_DROPOUT="${ASI3_LORA_DROPOUT:-0.05}"
TARGET_MODULES="${ASI3_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
MIN_TRAINABLE_PARAMETERS="${ASI3_MIN_TRAINABLE_PARAMETERS:-5000000}"
MAX_TRAINABLE_PARAMETERS="${ASI3_MAX_TRAINABLE_PARAMETERS:-2000000000}"

cd "$REMOTE_ROOT"

echo "__ASI3_SCENARIO_LORA_START__"
date -u +"%Y-%m-%dT%H:%M:%SZ"
python3 --version

# ---- max-steps = ceil(examples / (grad_accum * world_size)) * epochs ---------
# Single-process sharded run => world_size == 1.
TRAIN_COUNT="$(wc -l < "$TRAIN_FILE" | tr -d '[:space:]')"
if [[ "$TRAIN_COUNT" -le 0 ]]; then
  echo "ERROR: empty train file: $TRAIN_FILE" >&2
  exit 1
fi
MAX_STEPS="${ASI3_MAX_STEPS:-$(( (TRAIN_COUNT + GRAD_ACCUM - 1) / GRAD_ACCUM ))}"
if [[ "$MAX_STEPS" -lt 1 ]]; then MAX_STEPS=1; fi
echo "train_examples=$TRAIN_COUNT grad_accum=$GRAD_ACCUM => max_steps=$MAX_STEPS (1 epoch)"

# ---- deps -------------------------------------------------------------------
pip3 install -q peft accelerate huggingface_hub compressed-tensors 2>/dev/null || \
  pip3 install peft accelerate huggingface_hub compressed-tensors

# ---- sanity -----------------------------------------------------------------
test -d "$MODEL_NAME"                       || { echo "ERROR: model dir missing: $MODEL_NAME" >&2; exit 1; }
test -s training/qwen_sft_peft.py           || { echo "ERROR: trainer missing" >&2; exit 1; }
test -s training/dequantize_moe_w8a8_to_bf16.py || { echo "ERROR: dequant script missing" >&2; exit 1; }
test -s "$TRAIN_FILE"                        || { echo "ERROR: train file missing: $TRAIN_FILE" >&2; exit 1; }

mkdir -p logs reports

# ---- decompress W8A8 -> bf16 -------------------------------------------------
echo "__DECOMPRESS_START__"
if [[ -d "$DECOMPRESSED_MODEL_PATH" && -f "$DECOMPRESSED_DONE_MARKER" ]]; then
  echo "__DECOMPRESS_CACHED__ $DECOMPRESSED_MODEL_PATH"
else
  rm -f "$DECOMPRESSED_DONE_MARKER"
  python3 training/dequantize_moe_w8a8_to_bf16.py \
    --input-dir "$MODEL_NAME" --output-dir "$DECOMPRESSED_MODEL_PATH"
  test -f "$DECOMPRESSED_DONE_MARKER" || { echo "__DECOMPRESS_FAILED__" >&2; exit 1; }
fi
echo "__DECOMPRESS_OK__ $DECOMPRESSED_MODEL_PATH"

# ---- launch -----------------------------------------------------------------
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false

echo "__ASI3_BEFORE_TRAIN__ visible_npus=${ASCEND_RT_VISIBLE_DEVICES:-<all>}"
python3 training/qwen_sft_peft.py \
  --model-name "$DECOMPRESSED_MODEL_PATH" \
  --train-file "$TRAIN_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB" \
  --max-length "$MAX_LENGTH" \
  --max-steps "$MAX_STEPS" \
  --num-epochs "$NUM_EPOCHS" \
  --per-device-batch-size "$PER_DEVICE_BATCH_SIZE" \
  --gradient-accumulation-steps "$GRAD_ACCUM" \
  --learning-rate "$LEARNING_RATE" \
  --log-steps "$LOG_STEPS" \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --lora-dropout "$LORA_DROPOUT" \
  --target-modules $TARGET_MODULES \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters "$MIN_TRAINABLE_PARAMETERS" \
  --max-trainable-parameters "$MAX_TRAINABLE_PARAMETERS" \
  2>&1 | tee "$LOG_PATH"
echo "__ASI3_AFTER_TRAIN__"

test -f "$OUTPUT_DIR/metrics.json" || { echo "ERROR: metrics.json missing" >&2; exit 1; }
test -d "$OUTPUT_DIR/adapter"      || { echo "ERROR: adapter dir missing" >&2; exit 1; }
cp "$OUTPUT_DIR/metrics.json" reports/asi3_qwen36_35b_scenario_lora_metrics.json
python3 -c "import json; m=json.load(open('$OUTPUT_DIR/metrics.json')); print('trainable_params:', m.get('trainable_parameter_count')); print('completed_steps:', m.get('completed_steps')); print('final_eval:', m.get('final_eval'))"
echo "__ASI3_SCENARIO_LORA_DONE__"

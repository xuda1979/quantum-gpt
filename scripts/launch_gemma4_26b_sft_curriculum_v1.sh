#!/usr/bin/env bash
# Launch Gemma 4 26B-A4B-it SFT with the full curriculum-mix-v1 dataset (9294 train rows).
#
# Dataset: data/generated/gemma4-curriculum-mix-v1
#   - gemma4-quantum-full-v1-enriched: 31 quantum + 11 software tasks, 96 variants each
#   - quantum hard boost: 2x repeat on quantum-domain rows
#   - paper warmup + paper smoke: research-paper QA data (3x + 4x repeats)
#   - semantic software: interface-prefix-semantic-v4 (2x repeat)
#
# This is ~3x more data than the previous best run (qwen25-strict-recovery-curriculum-v2-enriched, 3093 rows).
#
# Usage (local CPU smoke):
#   bash scripts/launch_gemma4_26b_sft_curriculum_v1.sh --device cpu --max-steps 2
#
# Usage (8 NPU):
#   ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
#   torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
#     ... (see the rendered command below)
set -euo pipefail

DEVICE="${DEVICE:-cpu}"
MAX_STEPS="${MAX_STEPS:-80}"
EVAL_STEPS="${EVAL_STEPS:-20}"
LOG_STEPS="${LOG_STEPS:-5}"
NUM_EPOCHS="${NUM_EPOCHS:-2}"
GRAD_ACCUM="${GRAD_ACCUM:-4}"
LR="${LR:-1.5e-4}"
MAX_LENGTH="${MAX_LENGTH:-1024}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
BATCH_SIZE="${BATCH_SIZE:-1}"

MODEL_NAME="models/gemma-4-26B-A4B-it"
TRAIN_FILE="data/generated/gemma4-curriculum-mix-v1/train.jsonl"
EVAL_FILE="data/generated/gemma4-curriculum-mix-v1/eval.jsonl"
TIMESTAMP="$(date +%Y%m%dT%H%M)"
OUTPUT_DIR="outputs/gemma4-26b-a4b-it-curriculum-sft-v1-${TIMESTAMP}"

# Override from CLI
while [[ $# -gt 0 ]]; do
  case "$1" in
    --device) DEVICE="$2"; shift 2 ;;
    --max-steps) MAX_STEPS="$2"; shift 2 ;;
    --eval-steps) EVAL_STEPS="$2"; shift 2 ;;
    --log-steps) LOG_STEPS="$2"; shift 2 ;;
    --num-epochs) NUM_EPOCHS="$2"; shift 2 ;;
    --grad-accum) GRAD_ACCUM="$2"; shift 2 ;;
    --lr) LR="$2"; shift 2 ;;
    --max-length) MAX_LENGTH="$2"; shift 2 ;;
    --lora-rank) LORA_RANK="$2"; shift 2 ;;
    --lora-alpha) LORA_ALPHA="$2"; shift 2 ;;
    --batch-size) BATCH_SIZE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

echo "=== Gemma 4 26B-A4B-it SFT: curriculum-mix-v1 ==="
echo "  model:      $MODEL_NAME"
echo "  train_file:  $TRAIN_FILE ($(wc -l < "$TRAIN_FILE") rows)"
echo "  eval_file:   $EVAL_FILE ($(wc -l < "$EVAL_FILE") rows)"
echo "  output_dir:  $OUTPUT_DIR"
echo "  device:      $DEVICE"
echo "  max_steps:   $MAX_STEPS"
echo "  num_epochs:  $NUM_EPOCHS"
echo "  grad_accum:  $GRAD_ACCUM"
echo "  lr:          $LR"
echo "  max_length:  $MAX_LENGTH"
echo "  lora_rank:   $LORA_RANK"
echo "  lora_alpha:  $LORA_ALPHA"
echo ""

exec python3 training/qwen_sft_peft.py \
  --model-name "$MODEL_NAME" \
  --train-file "$TRAIN_FILE" \
  --eval-file "$EVAL_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --device "$DEVICE" \
  --max-length "$MAX_LENGTH" \
  --per-device-batch-size "$BATCH_SIZE" \
  --gradient-accumulation-steps "$GRAD_ACCUM" \
  --learning-rate "$LR" \
  --num-epochs "$NUM_EPOCHS" \
  --max-steps "$MAX_STEPS" \
  --eval-steps "$EVAL_STEPS" \
  --log-steps "$LOG_STEPS" \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --train-on-completions-only \
  --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding

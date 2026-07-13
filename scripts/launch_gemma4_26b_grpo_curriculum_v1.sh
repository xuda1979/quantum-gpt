#!/usr/bin/env bash
# Launch Gemma 4 26B-A4B-it GRPO after SFT with curriculum-mix-v1.
#
# Assumes the SFT adapter from launch_gemma4_26b_sft_curriculum_v1.sh is available.
#
# Usage (local CPU smoke):
#   bash scripts/launch_gemma4_26b_grpo_curriculum_v1.sh --device cpu --grpo-steps 2 --adapter-init outputs/<latest>/adapter
#
# Usage (8 NPU):
#   ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
#   torchrun --nproc_per_node=8 --master_port=29531 training/grpo_trainer.py \
#     ... (see rendered command below)
set -euo pipefail

DEVICE="${DEVICE:-cpu}"
GRPO_STEPS="${GRPO_STEPS:-20}"
GROUP_SIZE="${GROUP_SIZE:-4}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-256}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-2048}"
TEMPERATURE="${TEMPERATURE:-0.7}"
LR="${LR:-5e-6}"
LOG_STEPS="${LOG_STEPS:-2}"
ADAPTER_INIT=""
BENCHMARK_FILE="evals/benchmarks/gemma4_quantum_generalization_holdout_v1.txt"

MODEL_NAME="models/gemma-4-26B-A4B-it"
TIMESTAMP="$(date +%Y%m%dT%H%M)"
OUTPUT_DIR="outputs/gemma4-26b-a4b-it-curriculum-grpo-v1-${TIMESTAMP}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device) DEVICE="$2"; shift 2 ;;
    --grpo-steps) GRPO_STEPS="$2"; shift 2 ;;
    --group-size) GROUP_SIZE="$2"; shift 2 ;;
    --max-new-tokens) MAX_NEW_TOKENS="$2"; shift 2 ;;
    --max-seq-length) MAX_SEQ_LENGTH="$2"; shift 2 ;;
    --temperature) TEMPERATURE="$2"; shift 2 ;;
    --lr) LR="$2"; shift 2 ;;
    --log-steps) LOG_STEPS="$2"; shift 2 ;;
    --adapter-init) ADAPTER_INIT="$2"; shift 2 ;;
    --benchmark-file) BENCHMARK_FILE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

echo "=== Gemma 4 26B-A4B-it GRPO: curriculum-v1 ==="
echo "  model:          $MODEL_NAME"
echo "  adapter_init:   ${ADAPTER_INIT:-none}"
echo "  benchmark_file: $BENCHMARK_FILE"
echo "  output_dir:     $OUTPUT_DIR"
echo "  device:         $DEVICE"
echo "  grpo_steps:     $GRPO_STEPS"
echo "  group_size:     $GROUP_SIZE"
echo "  temperature:    $TEMPERATURE"
echo ""

ADAPTER_ARG=""
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARG="--adapter-init $ADAPTER_INIT"
fi

exec python3 training/grpo_trainer.py \
  --model-name "$MODEL_NAME" \
  $ADAPTER_ARG \
  --benchmark-file "$BENCHMARK_FILE" \
  --domain-filter quantum \
  --output-dir "$OUTPUT_DIR" \
  --device "$DEVICE" \
  --group-size "$GROUP_SIZE" \
  --grpo-steps "$GRPO_STEPS" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-seq-length "$MAX_SEQ_LENGTH" \
  --temperature "$TEMPERATURE" \
  --lr "$LR" \
  --kl-coeff 0.05 \
  --reward-pass-weight 0.6 \
  --reward-syntax-weight 0.1 \
  --reward-interface-weight 0.15 \
  --reward-verifier-weight 0.15 \
  --ratio-clip-log-delta 4.0 \
  --logit-clip 30.0 \
  --min-reward-std 0.02 \
  --curriculum-ema-decay 0.8 \
  --curriculum-min-weight 0.1 \
  --quantum-priority 1.1 \
  --curriculum-uncertainty-bonus 0.2 \
  --log-steps "$LOG_STEPS" \
  --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding

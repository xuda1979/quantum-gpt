#!/usr/bin/env bash
set -euo pipefail

PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
  --model-name models/OmniCoder-9B \
  --train-file data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl \
  --eval-file data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl \
  --output-dir outputs/omnicoder9b-quantum-generalization-sft-8npu-true32 \
  --device npu \
  --max-length 512 \
  --max-steps 32 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 2 \
  --eval-steps 8 \
  --log-steps 1 \
  --train-on-completions-only \
  --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding

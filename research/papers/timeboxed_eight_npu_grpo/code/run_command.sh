#!/usr/bin/env bash
set -euo pipefail

PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
torchrun --nproc_per_node=8 training/grpo_trainer.py \
  --model-name models/OmniCoder-9B \
  --adapter-init outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter \
  --benchmark-file evals/benchmarks/quantum_generalization_holdout_v1.txt \
  --domain-filter quantum \
  --output-dir outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8 \
  --device npu \
  --group-size 4 \
  --grpo-steps 8 \
  --max-new-tokens 192 \
  --max-seq-length 3072 \
  --temperature 0.7 \
  --log-steps 1 \
  --lr 5e-6 \
  --ratio-clip-log-delta 4.0 \
  --logit-clip 30.0 \
  --min-reward-std 0.02 \
  --curriculum-ema-decay 0.8 \
  --curriculum-min-weight 0.1 \
  --quantum-priority 1.1 \
  --curriculum-uncertainty-bonus 0.2 \
  --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding

#!/usr/bin/env python3
"""Render leadership-ready 8-NPU timeboxed SFT/GRPO commands."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path("artifacts/timeboxed-8npu-scaleup-command-sheet.txt")

SFT_COMMAND = """PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \\
TOKENIZERS_PARALLELISM=false \\
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \\
torchrun --nproc_per_node=8 training/qwen_sft_peft.py \\
  --model-name models/OmniCoder-9B \\
  --adapter-init outputs/omnicoder9b-quantum-hard-v1-continue-true40-e2-20260330T142009CST/adapter \\
  --train-file data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl \\
  --eval-file data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl \\
  --output-dir outputs/omnicoder9b-quantum-generalization-sft-8npu-true40 \\
  --device npu \\
  --max-length 512 \\
  --per-device-batch-size 1 \\
  --gradient-accumulation-steps 2 \\
  --learning-rate 2e-4 \\
  --num-epochs 1 \\
  --max-steps 40 \\
  --eval-steps 1000 \\
  --log-steps 5 \\
  --train-on-completions-only \\
  --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding"""

GRPO_COMMAND = """PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \\
TOKENIZERS_PARALLELISM=false \\
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \\
torchrun --nproc_per_node=8 --master_port=29531 training/grpo_trainer.py \\
  --model-name models/OmniCoder-9B \\
  --adapter-init outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter \\
  --benchmark-file evals/benchmarks/quantum_generalization_holdout_v1.txt \\
  --domain-filter quantum \\
  --output-dir outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8 \\
  --device npu \\
  --group-size 4 \\
  --grpo-steps 8 \\
  --max-new-tokens 128 \\
  --max-seq-length 2048 \\
  --temperature 0.7 \\
  --lr 5e-6 \\
  --kl-coeff 0.05 \\
  --reward-pass-weight 0.6 \\
  --reward-syntax-weight 0.1 \\
  --reward-interface-weight 0.15 \\
  --reward-verifier-weight 0.15 \\
  --ratio-clip-log-delta 4.0 \\
  --logit-clip 30.0 \\
  --min-reward-std 0.02 \\
  --curriculum-ema-decay 0.8 \\
  --curriculum-min-weight 0.1 \\
  --quantum-priority 1.1 \\
  --curriculum-uncertainty-bonus 0.2 \\
  --log-steps 1 \\
  --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding"""


def main() -> int:
    payload = {
        "sft": SFT_COMMAND,
        "grpo": GRPO_COMMAND,
        "papers": [
            "research/papers/timeboxed_eight_npu_sft/paper.md",
            "research/papers/timeboxed_eight_npu_grpo/paper.md",
            "research/papers/verifier_guided_repair_curriculum/paper.md",
            "research/papers/clause_aware_verifier_reward/paper.md",
            "research/papers/ast_anchor_interface_grounding/paper.md",
            "research/papers/self_consistency_verifier_routing/paper.md",
            "research/papers/uncertainty_triggered_repair_replay/paper.md",
        ],
    }
    text = "\n".join(
        [
            "# Timeboxed 8-NPU Scale-Up Command Sheet",
            "# target: under 2 hours per run, leadership-facing, all 8 NPUs when available",
            "",
            "## SFT",
            SFT_COMMAND,
            "",
            "## GRPO",
            GRPO_COMMAND,
            "",
            "## JSON",
            json.dumps(payload, indent=2),
            "",
        ]
    )
    OUTPUT.write_text(text, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

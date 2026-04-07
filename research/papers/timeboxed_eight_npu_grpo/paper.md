# Timeboxed 8-NPU GRPO Scaling Plan

## Objective

Run a meaningful OmniCoder GRPO scale-up on all 8 NPUs while staying under a 2-hour wall-clock budget.

## Operating Assumptions

- Use `torchrun --nproc_per_node=8`
- Keep `max_new_tokens` bounded
- Use lower exploration and tighter stability clips than the failing tiny smokes
- Start from the current OmniCoder semantic-v4 adapter

## Proposed Run

- Base model: `models/OmniCoder-9B`
- Adapter init:
  - `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter`
- Benchmark:
  - `evals/benchmarks/quantum_generalization_holdout_v1.txt`
- Output:
  - `outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8`
- Suggested budget:
  - `group_size=4`
  - `grpo_steps=8`
  - `max_new_tokens=128`
  - `max_seq_length=2048`
  - `temperature=0.7`
  - `lr=5e-6`

## Rationale

- The runtime path is already fixed through smoke5
- Smoke6 recovered a real ai2 OOM at a looser sequence budget, so the timeboxed GRPO plan now caps rollout/context length more aggressively
- The current bottleneck is update yield, so this run favors stable, information-bearing updates over aggressive exploration
- 8 steps on all 8 NPUs is enough to show scaled RL activity without drifting into an unbounded overnight job

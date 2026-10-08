# Track N8 — QAOA-Cut-Value Calibration SFT (QCC-SFT)

**Owner:** subagent track (loop 2026-07-13, iteration 15:25)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-11 iter-2 gap report §3 item 6)

"QAOA p=1 cut value off" — qwen3.6-27b-rag outputs doc prose instead of a
code program on the QAOA cut-value tasks. Even when it emits code, the
computed MaxCut value is wrong (off by one edge, or wrong partition). This
overlaps with N6 (format) but targets the **numeric correctness** of the
cut-value computation, not the format.

## Approach

Build an SFT set of complete `def main()` programs that:

1. Construct a small graph (3-5 nodes, 4-6 edges).
2. Compute the MaxCut value by brute-force enumeration (not QAOA
   simulation — the *value* is what's tested).
3. Print the exact integer.

Each row is verified by executing the program and comparing stdout to the
brute-force answer. The set covers the 5-cycle graph (the QAOA scorecard
seed) plus 4 variants (path, star, complete-K4, random-6-node).

## Data source

- Seed task: `qaoa_maxcut_5cycle`, `qaoa_maxcut`, `bitstring_maxcut_landscape`,
  `maxcut_assignment_enumerator`, `maxcut_partition_ranker` from
  `evals/tasks/quantum/`.
- Variants: parameterized graph topologies generated programmatically.

## Success metric

On the QAOA / MaxCut family tasks in the 56-task scorecard, a QCC-SFT-LoRA
adapter (on base) must show **≥ 2 more correct cut-value outputs**
(currently 2/8 correct on the family), with no regression on passing tasks.

## Out of scope

- Any NPU run.
- Modifying the SFT trainer.
- QAOA *parameter optimization* (this track targets cut-value *computation*,
  not ansatz tuning).

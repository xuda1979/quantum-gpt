# Track N2 — Quantum-Critic LoRA (teacher-free verifier)

**Owner:** subagent track (loop 2026-07-13)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem

Current RL + soft-distill loop depends on the GLM5.2 HTTP teacher for grading
and correction. The teacher is the throughput bottleneck and a single point
of failure. If we had a **small critic LoRA** on the same Qwen3.6 base that
could grade a candidate quantum program against a rubric, we could:
1. Run RL-with-critic without any external teacher call.
2. Multiply the effective reward-signal throughput by ~10× (local NPU vs.
   HTTP round-trip).
3. Use the critic as a `pass@1` filter at *inference* time, not just training.

## Idea (post-training only)

Train a **critic LoRA** on the same Qwen3.6-27B base, with the input/output
contract:

- Input: `{task_spec, candidate_code, rubric}` (rubric from
  `configs/rl/reward_rubric_v1.json`).
- Output: JSON `{"pass": bool, "scores": {...}, "reasoning": "..."}`.

Training data is already on disk:
- Positive examples: `evals/tasks/quantum/*/candidate.py` (reference
  solutions) — paired with each task's `tests.py` passing → label `pass=true`.
- Negative examples: the failing roll-outs in
  `evals/subsystem/recommendations/*.json` — labeled with the actual failure
  mode from `tests.py` output → `pass=false` + the ImportError/prose/timeout
  reasoning.

This is **pure SFT** (no RL needed to bootstrap the critic), and the data is
already verified.

## Scaffold plan (this track produces)

1. `docs/rd-line-quantum-critic-lora-2026-07-13.md` — full design doc,
   including the critic I/O contract and how it plugs into
   `scripts/rl_distill_pipeline.py` as an alternative to the GLM5.2 grade
   step.
2. `scripts/prepare_critic_sft.py` — walks `evals/tasks/quantum/` + the
   recommendation JSONs, emits ChatML SFT rows with the critic I/O contract.
3. `configs/sft/qwen36_critic_lora_v1.json` — SFT config for the critic
   LoRA; `sequence_length=4096` (critic inputs are short), `epochs=2`.
4. `tests/test_prepare_critic_sft.py` — asserts every emitted row has the
   required JSON schema on the assistant side and a non-empty `reasoning`
   field.

## Success metric

Critic-LoRA, evaluated on a held-out 20% split of the 56-task QAOA scorecard,
must achieve ≥ 85% agreement with the *execution-grounded* pass/fail label
from `tests.py`. (Random = 50%; GLM5.2 teacher agreement with execution is
~92% per `docs/rl-distill-iteration-process-2026-07.md`.)

## Out of scope

- Replacing the GLM5.2 teacher in the live RL loop (this track only produces
  the critic; wiring it into `scripts/rl_distill_pipeline.py` is a follow-up
  once the 85% agreement is verified).
- Any NPU run.
- Modifying the RL trainer.

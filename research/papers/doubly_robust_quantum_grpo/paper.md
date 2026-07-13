# Doubly-Robust GRPO for Quantum Code Generation

A hybrid DPO + PPO alignment recipe that applies doubly-robust (DR)
advantage estimation to Group Relative Policy Optimization (GRPO) on
verifiable quantum-coding rewards. The target workload is the
Qiskit-HumanEval-style benchmark family already living under
`evals/tasks/quantum/` and `evals/benchmarks/`, where every task
exposes a deterministic `tests.py` that produces a binary pass / fail
plus a structured failure list.

## Why this paper exists

The current RL stack (`training/grpo_trainer.py`,
`training/grpo_utils.py:stable_grpo_loss`) computes a single-sample
PPO-style clipped surrogate with an implicit group-mean advantage. On
the quantum-coding workload this gives three recurring problems:

1. **High variance advantage on small groups.** With `group_size=4`
   and a binary pass reward, the within-group advantage for an all-fail
   or all-pass group is exactly zero, so the step is dropped as a
   `low_reward_signal` skip. The existing curriculum already throws
   away a large fraction of steps this way.
2. **Reference-model drift.** PPO and GRPO both rely on a stale
   `old_log_probs` snapshot as the behavior policy. Across a long
   multi-round run (the ASI1 2-NPU loop already runs for hours), the
   gap between the snapshot and the live LoRA weights grows, and the
   importance ratio `r = exp(log_pi - log_pi_old)` becomes a biased
   estimator of the true policy ratio.
3. **No use of preference pairs.** The repo already collects
   verifier-produced `(chosen, rejected)` pairs every GRPO step (passing
   candidates vs. failing candidates inside the same group). Those
   pairs are currently discarded. DPO and DR-alignment give a
   reference-free way to consume them, but a pure DPO update ignores
   the verifiable reward signal and a pure PPO update ignores the
   pairwise structure.

## Core idea

Treat each GRPO group as a small preference dataset and estimate the
policy gradient with a **doubly-robust** combination of:

- a PPO/GRPO control variate `(r * A)`, where `A` is the group-mean
  baseline advantage (the existing path), and
- a DPO-style pairwise score `beta * (log_pi(chosen) - log_pi(rejected))`
  that is unbiased for any fixed pair drawn from the same group.

The DR estimator (cite arXiv:2406.14712 / Doubly Robust Alignment for
LLMs) is

    L_DR = (1/N) sum_i [ r_i * A_i - psi * (r_i - 1) * A_i ]
         + (beta / |P|) sum_(c,r) in P [ -log sigmoid(beta * (s(c) - s(r))) ]

where:

- `r_i = exp(log_pi_theta(y_i|x_i) - log_pi_old(y_i|x_i))` is the
  usual PPO ratio,
- `A_i = R_i - mean_group(R)` is the centered advantage already used
  by GRPO,
- `psi` is a learned / tuned regression coefficient that minimizes the
  variance of the DR estimator,
- `P` is the set of `(chosen, rejected)` pairs mined from the same
  group (one pair per group when both exist, ranked by reward gap),
- `s(y) = log_pi_theta(y|x) - log_pi_ref(y|x)` is the DPO implicit
  reward, with `log_pi_ref` either the LoRA-off value (cheap) or a
  frozen snapshot (default).

The first term reduces to the existing GRPO loss when `psi = 0`. The
second term is the standard DPO loss with one pair per group. The DR
combination is unbiased for the true policy gradient whenever either
(a) the PPO ratio is exactly correct (`psi` arbitrary) or (b) the DPO
pair model is correctly specified (`psi = 1`); this is the standard
DR property.

## Why it matters for this project

- **Recovers skipped steps.** Even when a group has zero reward
  variance (today's `low_reward_signal` skip), if at least one
  candidate passes and one fails, the DPO term still produces a
  non-zero gradient. This directly attacks the biggest source of
  wasted NPU time in the current ASI1 2-NPU loop.
- **Lower-variance RL on small groups.** The DR correction term
  `(r - 1) * A` has zero mean but reduces variance when the behavior
  policy is close to the target, which is exactly the regime where
  LoRA + small `lr` lives.
- **Reuses existing infrastructure.** No new trainer is required: this
  is a research plugin that contributes a reward-shaping term
  (`adjust_reward_breakdown`) and an extra run-config block. The
  pairwise gradient is implemented as a second backward over the same
  forward logits already computed by `stable_grpo_loss`, so it costs
  one extra backward per step on 2 NPUs.
- **Leadership story.** "We combine PPO and DPO with a doubly-robust
  estimator to recover learning signal from verifier-evaluated
  quantum-coding tasks, evaluated on a Qiskit-HumanEval-style
  benchmark." This is a single-sentence claim that maps to a concrete
  plugin and a concrete 2-NPU run.

## Initial implementation

The plugin (`code/plugin.py`) exposes:

- `method_id = "doubly_robust_quantum_grpo"`
- `extra_run_config()` returns `{"dr_dpo_beta": 0.07,
  "dr_psi_init": 0.5, "dr_pair_min_reward_gap": 0.4,
  "dr_pair_loss_weight": 0.3, "dr_pair_max_per_step": 1,
  "dr_pair_buffer_path": null}`. The trainer reads these from the
  research-methods manifest.
- `adjust_reward_breakdown()` adds three new fields to each
  candidate's reward dict:
  - `dr_pair_role`: `"chosen"`, `"rejected"`, or `null` (when the
    candidate is not selected for a pair this step)
  - `dr_pair_partner_idx`: index of the partner candidate inside the
    same group (or `-1`)
  - `dr_pair_reward_gap`: absolute reward gap to the partner
- `augment_grpo_prompt()` appends a one-line instruction
  ("Prefer code that is most likely to pass the verifier on the first
  try; if uncertain, prefer the simpler, more readable variant.") that
  matches the DPO assumption that `chosen` and `rejected` come from
  the same prompt.
- `adjust_task_weight()` boosts tasks whose `behavior_hints` and
  `required_interface` are rich enough to make pair-mining meaningful
  (i.e. the task has more than one verifier-checked requirement).

A separate helper module (`code/dr_pair_loss.py`) implements the
pairwise DPO loss given a list of `(chosen_logprob, rejected_logprob,
ref_chosen_logprob, ref_rejected_logprob)` tuples. This helper is
intended to be called by `training/grpo_trainer.py` after the existing
PPO backward, but only when `--research-methods
doubly_robust_quantum_grpo` is passed. The trainer change is wrapped
behind a `try / import` so the plugin can be enabled without
modifying the base trainer for non-DR runs.

### Trainer integration status (2026-07-09)

The `training/grpo_trainer.py` loop now wires in **both** DR terms
when the plugin is enabled:

1. **DPO pair-loss term** — `compute_dr_pair_loss()` mines one
   `(chosen, rejected)` pair per group (ranked by reward gap, min gap
   `dr_pair_min_reward_gap = 0.4`) and adds
   `dr_pair_loss_weight * L_DPO` to `total_loss`.
2. **PPO-side variance-correction term** —
   `compute_dr_variance_correction()` adds
   `psi * E[(r - 1) * A]` to `total_loss`, where `r` is the PPO
   importance ratio (clipped to `ratio_clip_log_delta`) and `A` is
   the detached group-relative advantage. `psi = dr_psi_init = 0.5`
   by default.

Both terms are no-ops when the plugin is absent or when their
hyperparameters are zero, so base GRPO is unchanged. Each step record
in `grpo_step_metrics.jsonl` now carries `dr_pair_*` and
`dr_variance_correction_value` / `dr_psi` fields for offline
analysis. The full test suite
(`tests/test_doubly_robust_quantum_grpo.py`, 20 tests) covers the
plugin, the helper, and both trainer hooks.

## What this paper does NOT claim

- It does **not** claim a new state-of-the-art on the public Qiskit
  HumanEval benchmark. The repo's local quantum task suite
  (`evals/tasks/quantum/`, 37 tasks) is the evaluation surface; the
  Qiskit-HumanEval-style framing is the methodology, not the
  leaderboard.
- It does **not** change the GRPO trainer's core update. The base
  `stable_grpo_loss` is preserved. DR is an *additive* loss term with
  its own scaling, so a bad `psi` value can at worst slow convergence
  rather than break it.
- It does **not** depend on a remote teacher. Distillation pairs are
  already covered by `training/qwen_sft_peft_kl.py`; this paper is
  orthogonal and only consumes in-group verifier signals.

## Evaluation plan

The plan is to A/B the base GRPO run against `--research-methods
doubly_robust_quantum_grpo` on:

1. The existing 12-task quantum pass@1 slice
   (`evals/runs/iter2-pull/eval-27b-glm52-distill-iter2-pass1-12task-20260706T115000Z.json`
   is the iter-2 baseline).
2. The multi-framework holdout
   (`evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt`),
   which is the closest local analog to the Qiskit-HumanEval
   multi-task coverage.
3. The disjoint training benchmark
   (`evals/benchmarks/quantum_grpo_training_v2_disjoint.txt`), used
   as the *training* set so the eval sets stay disjoint.

Success criterion: the DR run reaches the same pass@1 as the base
GRPO run in <= 60% of the wall-clock steps (i.e. the
`low_reward_signal` skip rate drops and the per-step gradient norm
stays finite). Failure criterion: if the DR pair loss produces NaN
or does not reduce the skip rate within 50 steps, the plugin is
disabled and the run continues with base GRPO.

## Fast-abandon rule

Drop this method if any of these hold:

1. The DR pair loss is consistently NaN or > 10x the PPO loss after
   `psi` warmup (10 steps). This means the pair-mining is producing
   bad pairs or the implicit reward gap is too large.
2. The skip rate does not drop by at least 25% relative to a base
   GRPO run on the same 50-step window. The whole point is to recover
   skipped steps; if it does not, the extra backward is wasted.
3. The DR run's pass@1 on the 12-task slice is below the base run by
   more than 5 percentage points after 100 steps. The DR correction
   should never hurt the final metric.

## Operating discipline

- Default `dr_dpo_beta = 0.07` matches `configs/dpo/qwen36_35b_a3b_dpo_v1.json`.
- Default `dr_pair_loss_weight = 0.3` is conservative; the PPO loss
  still dominates.
- Default `dr_psi_init = 0.5` is the midpoint of the DR range. Tune
  after step 50 if variance is too high.
- Pair-mining requires a minimum reward gap of 0.4 to avoid using
  near-tied pairs (which would inject noise).
- At most one pair per group per step (`dr_pair_max_per_step = 1`)
  to keep the extra backward cost predictable.

## Target hardware

This is designed for the ASI1 2-NPU configuration already used by
`scripts/asi1_launch_rl_distill_27b_2npu.sh`:

- 2x Ascend 910B2 (60.96 GiB each)
- Qwen3.6-27B student with LoRA rank 16
- vLLM serve on NPU 0,1, port 8007
- Trainer on NPU 0,1 with `torchrun --nproc_per_node=2`

The DR pair loss is computed on the same device as the PPO loss and
adds roughly one extra backward per step. On 2 NPUs this is
acceptable because the existing PPO backward is already
compute-bound on the small group size. On 8 NPUs the extra backward
would be amortized across devices, so the plugin is also safe to
enable there.

## Files produced by this paper

- `research/papers/doubly_robust_quantum_grpo/paper.md` (this file)
- `research/papers/doubly_robust_quantum_grpo/code/plugin.py` (the
  research-method plugin)
- `research/papers/doubly_robust_quantum_grpo/code/dr_pair_loss.py`
  (pairwise DPO loss helper, used by the trainer when the plugin is
  enabled)
- `research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh`
  (ASI1 2-NPU launcher that wraps the existing
  `asi1_launch_rl_distill_27b_2npu.sh` with the
  `--research-methods doubly_robust_quantum_grpo` flag and the DR
  config block)
- `research/papers/doubly_robust_quantum_grpo/code/README.md`
  (operator runbook)

## References

- Proximal Policy Optimization Algorithms, Schulman et al., 2017
  (arXiv:1707.06347) — the PPO clipped surrogate that GRPO inherits.
- Direct Preference Optimization: Your Language Model is Secretly a
  Reward Model, Rafailov et al., 2023 (arXiv:2305.18290) — the
  pairwise DPO loss used as the second DR term.
- Doubly Robust Alignment for Large Language Models, 2024
  (arXiv:2506.01183) — the DR estimator that combines the PPO and
  DPO terms.
- Qiskit HumanEval: An Evaluation Benchmark For Quantum Code
  Generative Models, 2024 (arXiv:2406.14712) — the public
  quantum-coding benchmark family whose methodology we mirror with
  the local `evals/tasks/quantum/` suite (37 verifier-checked tasks).
- Less Training Data and Smaller Model Sizes: the broader
  small-model alignment literature that motivates doing this on a
  27B student with LoRA instead of a 70B+ full fine-tune.

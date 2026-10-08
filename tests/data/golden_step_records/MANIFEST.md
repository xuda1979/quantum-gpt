# Golden SAPO step records (frozen corpus)

Captured 2026-08-31 from `tmp/math-watch/` (the same 29 records the
2026-08-26 math re-audit used), frozen for golden-log differential testing
(bug-hunter mechanism 2).

Source runs:
- `sapo-27b-ai-20260826T093441.jsonl` — 20 records (run-3 era, steps 1-20)
- `sapo-27b-ai-20260826T203454.jsonl` — 9 records (run-13 era, steps 1-9)

Every record carries the 2026-08-25 instrumentation fields
(`per_candidate_losses`, `loss_breakdown.loss_recomputed`,
`loss_reduction`, `rollout_rewards`) plus the 2026-08-26 r18 per-candidate
advantage terms (`mean_other`, `loo_raw`, `adv_scale`).

## Pinned identities (replayed by tests/test_golden_step_record_replay.py
through the CURRENT production code, not the independent auditor)

1. `Σ_i w_i·loss_i == loss_breakdown.loss_recomputed` (w_i = 1/G) — via
   `training.grpo_trainer.recompute_aggregate_sapo_loss`.
2. `loss == loss_recomputed + entropy_floor_penalty (+ DR terms)`.
3. `mean(total_reward) == mean_reward`.
4. LOO advantage terms: `mean_other == (Σr − r_i)/(G−1)`, `loo_raw == r_i −
   mean_other`, and `advantage == loo_raw/adv_scale` when unscaled-clamped
   (clamped candidates share |advantage| == clip bound).

Any drift = a production fix changed the math; investigate before landing.

## Schema contract

Fields the replay depends on (missing/renamed field = RED):
- top-level: `per_candidate_losses`, `loss_breakdown`, `rollout_rewards`,
  `mean_reward`, `loss`, `advantage_scale`
- `per_candidate_losses[i]`: `loss`, `weight`
- `loss_breakdown`: `loss_recomputed`, `entropy_floor_penalty`,
  `dr_pair_loss_added`, `dr_variance_correction_added`
- `rollout_rewards[i]`: `total_reward`, `advantage`

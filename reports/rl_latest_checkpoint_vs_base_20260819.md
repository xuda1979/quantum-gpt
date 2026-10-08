# Latest RL Checkpoint vs Base — Eval & Health Report (2026-08-19)

**Date**: 2026-08-19 | **Env**: ASI2 | **Base**: Qwen3.6-27B (`/root/work/filestorage/Qwen3.6-27B`)
**Latest RL checkpoint adapter**: `outputs/grpo-27b-selfeval-20260818T072721/adapter` (LoRA r=16 α=32)
**Evaluator**: `run_asi2_base_adapter_rubric_eval.py` (12 held-out tasks: 8 quantum + 4 software; exec pass@1 + static rubric + heldout CE loss)
**Eval output**: `outputs/reeval_latest_20260818T072721.json` (created 2026-08-19T09:48:52Z)

## Result: latest RL checkpoint == base (adapter still a no-op)

| Metric | Base | RL-Checkpoint Adapter | Delta |
|--------|------|----------------------|-------|
| Exec pass@1 (12 tasks) | 10/12 | 10/12 | 0 |
| overall rubric | 4.177 | 4.177 | 0 |
| grammar / algorithm / quality / efficiency | 4.167/4.167/4.025/4.333 | 4.167/4.167/4.025/4.333 | 0 |
| by_domain (quantum/software) | 6/8 & 4/4 | 6/8 & 4/4 | 0 |
| heldout CE loss (20 ex) | 1.9640155 | 1.9635103 | ~4e-4 (tiny) |
| heldout perplexity | 7.1278918 | 7.1242919 | ~0 |

The newest RL-produced adapter yields **identical pass@1 and identical rubric scores** to base. The heldout
loss differs only in the 4th decimal (much smaller than the Adapter B-matrix weight scale ~2e-4 would suggest),
so the checkpoint has **no functional effect on the model**. This matches the Aug 16 finding — RL still is not
producing task-level improvement.

## RL training status: STOPPED / NOT HEALTHY

- `bash scripts/asi2_launch_grpo_27b_selfeval.sh status` → **GRPO trainer: STOPPED** (pid file stale).
- No trainer process; `npu-smi` shows all 4x 910B2 NPUs **idle / no running processes**.
- Last real run: `grpo-27b-selfeval-20260818T072721`, last log `grpo_train_20260818T072721.log`, halted
  **at step 40/500** on 2026-08-18 by the `all_fail_without_repair` circuit breaker
  ("all-fail rollout share exceeds 40% without repair conversion").
- NAS checkpoints last synced 2026-08-18T15:27 (stale, no live sync).

## Why it halted (mechanical cause — fixable)

The FV-GSPO **repair stage was not wired into the trainer** during the 2026-08-18 launch:
`run_config.json` shows `repair_converted_jsonl = None`. So `count_repair_conversions()` returned 0 for the
entire run roughly, and the `all_fail_without_repair` breaker false-tripped at step 40 (the launch script's own
header comment warns exactly about this).

The repair stage was *subsequently* run on 2026-08-19T07:59 and produced 3 verified conversions:
`outputs/grpo-27b-selfeval-20260818T072721/repair_stage/repair_converted.jsonl` (3 lines) plus
`repair_sft.jsonl` / `repair_dpo.jsonl`. **Wiring this path on relaunch would unblock the breaker.**

## Root-cause status: zero-gradient bug fixed, but adapter still degenerate

- 2026-08-16 report diagnosed **zero-gradient-by-construction** (old_log_probs == current_log_probs → ratio=1
  → loss≈0 → LoRA never moved; adapter bit-identical to base).
- 2026-08-17 fix: `--inner-epochs` (default 2) implemented in `training/grpo_trainer.py` and validated
  (inner_epoch-1 loss = 1.13e-4, seq_kl=-2.1e-3, ratio=1.0021). Local == remote md5
  `7af230eb1c0c7b2f6b03e2c0af179d2a` (verified 2026-08-19).
- The 2026-08-18 run used this fixed trainer: losses are now **nonzero** (~1e-5 to ~5e-5, vs 1e-8 before) and
  `seq_kl`/`ratio_mean` are nonzero — so the pure zero-gradient bug is behind us.
- **However**, the observed `loss` is still tiny (~1e-5) and the final adapter is still a no-op. Per-step policy
  movement is negligible because LR=2e-6 with very tight GSPO clip bounds (0.0003/0.0004) and the run was cut
  short at 40 steps by the false-trip breaker. Metrics show `pass_rate ≈ 0` for ~all steps and
  `clip_high_fraction` frequently 0.75 (policy pinned at the clip ceiling).

## Decision: DO NOT relaunch as-is

Consistent with the eval-cron guardrail ("do not relaunch broken training until the root-cause fix is
validated") and the prior Aug-17 pattern: launching the same config again (even with repair wired) would
consume 8 NPUs for many hours only to most likely reproduce another base==adapter checkpoint (tiny per-step
updates × all-fail hard tasks). A blind relaunch is not an improvement.

## Required fix before relaunch (next step for the 5h loop)

1. **Wire repair feedback** into the trainer: launch with
   `REPAIR_CONVERTED_JSONL=<out>/repair_stage/repair_converted.jsonl` (already defaulted by the launch script)
   so the `all_fail_without_repair` breaker is unblocked by real conversions.
2. **Give the policy room to move**: the tight GSPO clips (0.0003/0.0004) + LR 2e-6 keep per-step updates
   negligible. Relax clip range (e.g. to ~1e-2..2e-1 or a GRPO-style 0.2/0.28) and/or raise LR, so a few
   hundred steps can actually shift the adapter off base.
3. **Validate on a short probe before an 8-NPU run**: run a short-steps probe and confirm adapter weights
   diverge from base and pass@1 on the held-out eval moves off 10/12 / rubric 4.177. Only then relaunch the
   full 500-step run.
4. Re-check `status` every 30 min / re-eval every 5h via the monitoring crons.

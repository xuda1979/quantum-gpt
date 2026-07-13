# Per-Artifact Scoring — Phase 5 NPU Ablation Runlist (2026-07-11)

**Status:** Runlist prepared. NOT submitted. Awaiting Huanxin transport
recovery (see `docs/huanxin-adapter-recovery-2026-07-11.md`) and a green
control run (Preset A) before launching treatment arms.

**Source plan:** `docs/per-artifact-scoring-rd-plan-2026-07-08.md` §5
**Launchers:** `scripts/asi1_launch_rl_distill_27b_2npu.sh`,
`scripts/asi2_launch_rl_distill_35b_2npu.sh`,
`scripts/asi3_launch_rl_distill_35b_2npu.sh`
**Training policy:** All runs submitted as Huanxin jobs (never on local/box NPU).

## Ablation presets (from plan §5)

| Preset | `--reward-weighted-nll` | `--per-artifact-kl-gate` | `--partial-credit-upweight` | Purpose |
|--------|:---:|:---:|:---:|---|
| `A_legacy` | off | off | 1.0 | control (legacy behavior) |
| `B_rw_nll` | on | off | 1.0 | reward-weighted NLL only |
| `C_kl_gate` | off | on | 1.0 | per-artifact KL gate only |
| `D_partial_up` | off | off | 0.5 | partial-credit upweight only |
| `E_full` | on | on | 0.5 | full treatment |
| `F_full_no_up` | on | on | 1.0 | full treatment minus partial upweight |

## Runlist — one row per (preset, student, launcher)

**Round budget:** `PIPELINE_MAX_ROUNDS=20` for all arms (per plan §5).
**Run-id convention:** `ablation-<preset>-<student>-<UTC-timestamp>`.

### Control (must complete first)

| # | Preset | Student | Launcher | Submit command |
|---|--------|---------|----------|----------------|
| 1 | `A_legacy` | ASI1 (27B) | `scripts/asi1_launch_rl_distill_27b_2npu.sh` | `ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=A_legacy PIPELINE_MAX_ROUNDS=20 RUN_ID=ablation-A-asi1-\$(date -u +%Y%m%dT%H%M%SZ) bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" bash scripts/submit_asi1_shell_task.sh --submit` |

### Treatment arms — ASI1 (27B)

| # | Preset | Student | Launcher | Submit command |
|---|--------|---------|----------|----------------|
| 2 | `B_rw_nll` | ASI1 (27B) | `scripts/asi1_launch_rl_distill_27b_2npu.sh` | `ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=B_rw_nll PIPELINE_MAX_ROUNDS=20 RUN_ID=ablation-B-asi1-\$(date -u +%Y%m%dT%H%M%SZ) bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" bash scripts/submit_asi1_shell_task.sh --submit` |
| 3 | `C_kl_gate` | ASI1 (27B) | same | substitute `ABLATION_PRESET=C_kl_gate` and `RUN_ID=ablation-C-asi1-...` |
| 4 | `D_partial_up` | ASI1 (27B) | same | substitute `ABLATION_PRESET=D_partial_up` and `RUN_ID=ablation-D-asi1-...` |
| 5 | `E_full` | ASI1 (27B) | same | substitute `ABLATION_PRESET=E_full` and `RUN_ID=ablation-E-asi1-...` |
| 6 | `F_full_no_up` | ASI1 (27B) | same | substitute `ABLATION_PRESET=F_full_no_up` and `RUN_ID=ablation-F-asi1-...` |

### Treatment arms — ASI3 (35B-A3B)

| # | Preset | Student | Launcher | Submit command |
|---|--------|---------|----------|----------------|
| 7 | `A_legacy` | ASI3 (35B) | `scripts/asi3_launch_rl_distill_35b_2npu.sh` | `ASI3_SHELL_REMOTE_COMMAND="ABLATION_PRESET=A_legacy PIPELINE_MAX_ROUNDS=20 RUN_ID=ablation-A-asi3-\$(date -u +%Y%m%dT%H%M%SZ) bash scripts/asi3_launch_rl_distill_35b_2npu.sh launch" bash scripts/submit_asi3_shell_task.sh --submit` |
| 8 | `B_rw_nll` | ASI3 (35B) | same | substitute `ABLATION_PRESET=B_rw_nll` and `RUN_ID=ablation-B-asi3-...` |
| 9 | `C_kl_gate` | ASI3 (35B) | same | substitute `ABLATION_PRESET=C_kl_gate` and `RUN_ID=ablation-C-asi3-...` |
| 10 | `D_partial_up` | ASI3 (35B) | same | substitute `ABLATION_PRESET=D_partial_up` and `RUN_ID=ablation-D-asi3-...` |
| 11 | `E_full` | ASI3 (35B) | same | substitute `ABLATION_PRESET=E_full` and `RUN_ID=ablation-E-asi3-...` |
| 12 | `F_full_no_up` | ASI3 (35B) | same | substitute `ABLATION_PRESET=F_full_no_up` and `RUN_ID=ablation-F-asi3-...` |

### Treatment arms — ASI2 (35B-A3B, second environment)

| # | Preset | Student | Launcher | Submit command |
|---|--------|---------|----------|----------------|
| 13–18 | `A_legacy`, `B_rw_nll`, `C_kl_gate`, `D_partial_up`, `E_full`, `F_full_no_up` | ASI2 (35B) | `scripts/asi2_launch_rl_distill_35b_2npu.sh` | same pattern, replacing `asi1`→`asi2` and using `scripts/submit_asi2_shell_task.sh --submit` |

**Total runs:** 18 (6 presets × 3 students). Each run uses 2 NPUs for
~20 rounds. Per plan §5, run sequentially within each student to avoid
NPU contention: A first, then B–F.

## Pre-submission checklist

- [ ] Huanxin transport verified (see `docs/huanxin-adapter-recovery-2026-07-11.md`)
- [ ] ASI1 / ASI3 base + iter-2 adapter states recovered (or decide to
      run ablation on base model only and document that)
- [ ] `outputs/eval-base-vs-adapter-asi1-iter2.json` exists (hard gate in
      `scripts/prepare_iter3_distill_sft.py` — though ablation runs don't
      strictly require this, the iter-3 build does)
- [ ] Local test suite green: `python3 -m pytest -x`
- [ ] `eval_gate` block wired into active RL config (`configs/rl/*.json`)
      per STATE.md "Immediate Next Steps" item 4

## During-run monitoring

- Pull `grpo_step_metrics.jsonl` from each run's output dir and run
  `python3 scripts/analyze_grpo_metrics.py --metrics <path>/grpo_step_metrics.jsonl --out-prefix <path>/grpo_metrics_analysis`
  to confirm `dr_variance_correction_value` stays finite and bounded
  (new analyzer added 2026-07-11).
- Watch for the "two consecutive regressions = hard stop" rule from
  the eval-discipline decision (STATE.md "Key Decisions").

## Post-run analysis

- Compare `pass@1` at round 20 for each preset vs. `A_legacy` on the same
  student. Success = at least one preset beats A without regressing on
  `pass@1` variance across 3 eval seeds (per plan §7).
- Write results into a new doc `docs/per-artifact-scoring-phase5-results-<date>.md`.

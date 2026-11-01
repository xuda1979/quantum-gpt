# Goal: SAPO adapter training with LLM-generated quantum tasks + fresh HARD 50-problem eval → 50/50 adapter

## Goal statement (verbatim, as armed + operator follow-up)
"using LLM harness to generate quantum computing coding tasks/problems to let adapter rollout
candidates in SAPO algorithm and keep training resuming the best adapter (18/18). create 50 new
evaluation problems(quality and diversity must be good). and evaluate checkpoints using the new
50 evaluation tasks."
Follow-up (2026-10-28): "keep working until we get a 50/50 adapter in the new 50-problem eval.
by the way, the 50 problems should be hard."
So: the 50 new eval problems must be HARD, diverse, high-quality; the loop continues until an
adapter reaches 50/50 on that suite.

## Checklist
- [x] 1. Read current SAPO loop state — DONE: champion = v22-resume step-1941 adapter
       (18/18 two-leg banked; sha 373b6e6d...), present on box at
       /root/work/quantum-gpt/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter.
       v22-resume run finished at step 3544 (lr 0.0, ended 2026-10-25). No training currently
       running on ASI1/ASI2. Taskgen: training/taskgen/ (51 families, mutation-checked tests,
       anti-leakage vs holdout-18, generator.py). Training data: outputs/C10605_v24_train_chatml.jsonl
       (4562 rows). Boxes: ASI2 stable/ready; ASI1+ASI3 daemons flapping/booting (watch gate).
- [ ] 2. Verify/launch training resuming the best adapter (18/18 champion v22-resume step-1941)
       on LLM-generated quantum tasks (resume → new run warm-continued from champion adapter).
- [ ] 3. Use the LLM harness (training/taskgen + LLM authoring) to generate HARD quantum coding
       tasks for rollouts with quality + diversity controls (dedupe vs all existing benchmarks,
       coverage across quantum subdomains, runnable/reference-checkable).
- [ ] 4. Create 50 NEW HARD evaluation problems (fresh eval suite: tasks + manifest + prompts +
       runner, compatible with existing eval harness; no leakage from training tasks).
- [ ] 5. Evaluate checkpoints (champion + base) on the new 50-problem eval; record baseline scores.
- [ ] 6. Iterate: mine failures → enrich SFT corpus from LLM-generated tasks → resume training
       from best adapter → re-eval until an adapter reaches 50/50 on the new suite.
- [ ] 7. Update STATUS; set Status: completed when a 50/50 adapter is banked with evidence.

## Status: in_progress

## Notes / uncertainty to resolve first
- Champion per recent commits: v22-resume step-1941, 18/18 on
  `sapo-holdout-enriched-contract-20260831T` (leg2 reconfirm banked; commit 0af206e74).
- Uncertainty: (a) exact current training/resume state — is a resume run active and which
  checkpoint is loaded; (b) how the LLM task generator is wired into SAPO rollouts;
  (c) eval suite format (manifest/problems/runner) so the new 50-problem suite plugs in.
- Prior goal (this file, previous content) is COMPLETED and archived in git history
  (7/18 v16 verification + leadership report). 18/18 line superseded it via v22-resume.

## Log
- 2026-10-28: Goal armed. Reading SAPO loop state next.
- 2026-10-28: Pre-change hygiene done (per operator directive): committed + pushed
  all 14 uncommitted tracked files as f26e273ea (harness fail-closed hardening
  batch: fixture-verdict quarantine, box-health gate, env-identity stamps,
  pinned base pass table, budget raise, STATUS log; UP031/E731 lint fixes;
  stale c10380 LaunchAgent unloaded + stray log removed). Remote main
  up to date; tree clean of tracked changes before starting goal work.
- 2026-10-28: Operator follow-up: 50 problems must be HARD; keep working until an
  adapter hits 50/50 on the new suite. Task 1 (read state) done.
- 2026-11-01: Current state snapshot (post-compaction resume):
  - C-10610 IBM QHE-139 dual-style base-vs-champion battery LIVE on ASI2:
    reconciler pid 25513 (--max-h 96), 114/164 tasks as of 11:50Z, ~10.8 t/h,
    ETA ~00:30 CST Nov 2. One box_down flap 09:46Z self-cleared. Journal:
    box /root/work/quantum-gpt outputs dir; local mirror logs/c10610_battery_reconciler.log.
    STATUS battery section committed as 64d83b433.
  - C-10611 v26 IBM-track corpus: 28/28 green, admitted, dual-style 56 rows
    (outputs/C10611_ibm_track_v26_spec.json; commit 550e7d904 batch).
  - C-10606 warm-continue card: READY but dispatch refused as budget-infeasible
    (~60 min vs 40-min slot). Options: budget bump or manager-direct launch
    (precedent c10452/c10601 manager_close pattern).
  - C-10612 SAPO RL dispatch on champion warm-start (28 admitted qg_* tasks):
    STAGED, on hold pending operator go. Do NOT launch without approval.
    Admission COMMITTED (373c9dd2f): 28/28 verified, 3/3 negatives rejected,
    sha-pinned manifest (outputs/C10611_rl_admission_manifest.json);
    reference_sha256 re-verified 28/28 OK at HEAD post-commit.
  - Post-battery TODO: re-run tasks 49–53 passed:false window (05:40–05:58Z,
    pre-matplotlib/networkx restore; check envelope stderr ImportError vs
    genuine fail); then base-vs-champion analysis on the 139 dual styles.
  - Goal items 4–7 (new-50 HARD eval suite → 50/50 iterate) remain the
    durable objective; C-10606/10610/10611/10612 are the supporting pipeline.

<!-- GENERATED from harness/contracts.py — DO NOT EDIT -->
# EVALUATOR — role card
Authority: run + verify holdout eval legs; read training artifacts; NEVER edit training code.

Invariants (from harness/contracts.py):
- [eval_leg_fail_closed] A leg without adapter-applied AND adapter-probe-differs markers is VOID — never score it.
  - enforced by: acceptance_gate.py, eval_watcher.py
- [eval_never_on_trainer_npu] Eval never runs on the trainer's NPUs.
  - enforced by: eval_watcher.py
- [eval_three_parallel_slices] Use 3 parallel task slices on ASI2 for holdout eval.
  - enforced by: eval_watcher.py
- [eval_verdict_location] Verdicts land in outputs/verdict_*.json (repo) and on the checkpoint bus.
  - enforced by: eval_watcher.py
- [eval_readonly_training_code] Evaluator reads training artifacts; NEVER edits training code.
  - enforced by: review checklist
- [probe_after_every_change] No claimed fix without a probe: every change lands with a deterministic probe artifact.
  - enforced by: tdd.py
- [box_ports_fixed] Box daemon ports are pinned in ONE config; scripts must import them, never re-declare.
  - enforced by: harness_config.py, lint_gate.py

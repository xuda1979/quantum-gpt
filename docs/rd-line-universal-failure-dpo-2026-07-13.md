# Track N1 — Universal-Failure Targeted DPO (UF-DPO)

**Owner:** subagent track (loop 2026-07-13)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-12 cross-ref)

`docs/iter3-gap-rec-crossref-2026-07-12.md` identifies **7 universal-gap tasks**
that fail on all 3 evaluated models (glm5.2, deepseek-v4-pro, qwen36-27b-rag)
on the QAOA 5-cycle 56-task scorecard. These are the highest-confidence
weaknesses — if a row closes one of these gaps, it is real signal, not noise.

## Idea (post-training only)

Build a **universal-failure DPO** dataset where every chosen/rejected pair is
grounded in one of the 7 universal-gap tasks:

- **Rejected** = an actual roll-out from the current best LoRA on that task
  (verified failing by `evals/subsystem/harness.py`).
- **Chosen** = a reference solution from `evals/tasks/quantum/qaoa_maxcut_5cycle/candidate.py`
  reformatted into the canonical assistant form (reusing the N6 formatter).

Because the chosen side is *machine-verified to pass*, this DPO pass cannot
teach the model to prefer a wrong answer — it can only sharpen the model's
preference toward the verified-correct program shape on tasks it currently
fails.

## Scaffold plan (this track produces)

1. `docs/rd-line-universal-failure-dpo-2026-07-13.md` — full design doc.
2. `scripts/prepare_universal_failure_dpo.py` — reads the 3 rec JSON files in
   `evals/subsystem/recommendations/`, intersects to 7 universal tasks, pairs
   each with the reference candidate, emits DPO JSONL.
3. `configs/dpo/qwen36_universal_failure_dpo_v1.json` — DPO config scoped to
   the 7 universal tasks; `beta=0.1` (sharper than baseline 0.07 because the
   chosen side is verified-correct, not just preferred).
4. `tests/test_prepare_universal_failure_dpo.py` — asserts every pair's
   chosen side runs and prints the expected output from the task's
   `tests.py`, and every rejected side is one of the 3 models' actual
   failing outputs.

## Success metric

Iter-3 eval must show **≥ 4 of the 7 universal-gap tasks now PASS** on at
least one of {27B-LoRA, 35B-LoRA}, with no regression on the 49 currently
passing tasks. (3 of 7 = baseline noise; 4 of 7 = real closure.)

## Out of scope

- Generating *new* GLM5.2 teacher corrections (teacher is a known bottleneck;
  this track deliberately uses only the reference candidate + failing
  roll-outs already on disk).
- Modifying the LoRA trainer.
- Any NPU run.

# Iter-3 Soft-Distillation SFT Dataset — Specification

**Date:** 2026-07-07
**Author:** Track B.1 (parallel session B)
**Status:** Spec & scaffold only. Training launch must wait for iter-2 eval results.
**Target students:** Qwen3.6-27B (ASI1, 2 NPUs), Qwen3.6-35B-A3B (ASI2/ASI3, 2 NPUs each)
**Teacher:** GLM5.2 (remote HTTP endpoint)

---

## 1. Why iter-3

Iter-2 (`data/generated/glm52_soft_distill_sft_iter2/`, 142 train / 13 eval)
was designed to fix the iter-1 ASI1 max_length=768 truncation (94.4% rows
truncated) and to add 5 gap topics (Cirq, PennyLane, error mitigation, QML,
ISQ/OpenQASM). The next iteration must be informed by **iter-2 eval results**
— which are not yet in hand — so this document only specifies the *scaffold*
and the *decision gates*; the actual row content is filled in after the
iter-2 base-vs-adapter report lands.

The high-level goal remains: lift pass@1 on the strict unseen quantum holdout
(`evals/benchmarks/quantum_generalization_holdout_v1.txt` and v2 hard) without
regressing general software-engineering pass@1.

## 2. Decision gates (must all pass before iter-3 build)

1. **Iter-2 eval complete.** `outputs/eval-base-vs-adapter-*` JSON exists for
   both ASI1 (27B) and ASI2/ASI3 (35B-A3B) iter-2 adapters.
2. **Failure taxonomy updated.** `evals/subsystem/dataset_gap.py recommend`
   produces a ranked gap list from the iter-2 eval JSONs.
3. **No regressions on software tasks.** The 12 standard software tasks
   (docstring_contract, off_by_one_bugfix, etc.) must not drop >5% pass@1
   vs. the iter-2 base.
4. **No max_length truncation.** Re-run the token-length audit from
   `docs/glm52-distillation-rd-iteration-process-2026-07.md` §Round 1 on the
   proposed iter-3 rows; require 0% truncation at the per-environment
   `max_length` (1600 for ASI1, 2048 for ASI2/ASI3).
5. **Train/eval disjointness.** No iter-3 eval task id may appear in any
   training split used since iter-1.

## 3. Composition target

| Slice | Rows (target) | Source | Purpose |
|---|---|---|---|
| Carry-forward from iter-2 | 142 | iter-2 train_chatml.jsonl (unchanged) | Preserve learned signal |
| New gap-targeted rows | 30–60 | GLM5.2 teacher corrections on iter-2 failure shapes | Fix diagnosed weaknesses |
| Multi-framework hard rows | 20–40 | New tasks in `evals/tasks/quantum/` (Track C.2) | Cirq/PennyLane/Braket coverage |
| Software-engineering retention | 20 | Existing `evals/tasks/software/` repaired as SFT | Prevent SWE regression |
| Eval (held-out) | 15–20 | New task ids not in any train split | Honest pass@1 signal |

Total train target: ~210–260 rows. This keeps the dataset in the
"small high-quality" regime validated by LIMA (NeurIPS 2023, arXiv:2305.11206)
while pushing the gap topics harder.

## 4. Per-environment training knobs (recommended starting point)

| Env | Base model | max_length | lr | adapter_init | LoRA r/a | target_modules |
|---|---|---|---|---|---|---|
| ASI1 | Qwen3.6-27B | 1600 | 3e-5 | iter-2 ASI1 adapter | 16 / 32 | q,k,v,o,gate,up,down |
| ASI2 | Qwen3.6-35B-A3B | 2048 | 5e-6 | iter-2 ASI2 adapter | 16 / 32 | q,k,v,o,gate,up,down |
| ASI3 | Qwen3.6-35B-A3B | 2048 | 5e-6 | iter-2 ASI3 adapter | 16 / 32 | q,k,v,o,gate,up,down |

Notes:
- ASI1 keeps the higher lr because the 27B base learns faster; ASI2/ASI3
  stay conservative to preserve the MoE expert routing learned in iter-2.
- `adapter_init` must point at the *evaluated* iter-2 adapter, not the last
  checkpoint, to avoid warm-starting from a possibly-diverged step.
- For MoE 35B-A3B, keep `target_modules` restricted to attention + MLP
  projections; do not LoRA the router (`gate`) at r=16 in iter-3 without
  a separate ablation.

## 5. Build pipeline (scaffold)

```
iter-2 eval JSON
   │
   ▼
evals/subsystem/dataset_gap.py recommend  ──→  gap report (JSON)
   │
   ▼
scripts/prepare_iter3_distill_sft.py build  ──→  data/generated/glm52_soft_distill_sft_iter3/
   │                                                ├── train_chatml.jsonl
   │                                                ├── eval_chatml.jsonl
   │                                                └── manifest.json
   ▼
3-round quality gate (structural / content / disjoint)
   │
   ▼
asi{1,2,3}_launch_glm52_distill_sft_*.sh  (existing iter-2 launchers, env-overridden)
```

The builder script `scripts/prepare_iter3_distill_sft.py` is scaffolded in
this same track. It accepts a gap-report JSON and a list of source JSONL
files, and produces deterministic, deduplicated train/eval splits with a
manifest recording provenance, per-row gap category, and per-row token
length.

## 6. Provenance & audit

Every iter-3 row carries:
- `example_id` (stable hash of messages content)
- `source` (one of: `iter2_carryforward`, `glm52_teacher_correction`,
  `multi_framework_task`, `swe_retention`)
- `gap_category` (from the gap report; `"none"` for carry-forward)
- `framework` (qiskit / cirq / pennylane / braket / none)
- `token_length` (computed with the Qwen3.6 tokenizer; required for the
  truncation audit)
- `teacher` (`glm5.2` for new rows; `inherit` for carry-forward)

The manifest records:
- `iteration: 3`
- `created`, `train_rows`, `eval_rows`
- `base_source` (iter-2 manifest path + sha256)
- `gap_report_source` (path to the dataset_gap.py output JSON)
- `quality_gates` (3 booleans, one per round)
- `recommended_training` (the table from §4, machine-readable)

## 7. Risk register

| Risk | Mitigation |
|---|---|
| Iter-2 eval shows no improvement over iter-1 | Do not build iter-3; instead diagnose whether the soft-distill loss is the bottleneck vs. the dataset. |
| New multi-framework rows are too hard and tank pass@1 | Cap hard rows at 20% of train; keep eval hard rows only in the held-out split. |
| 35B-A3B MoE adapter warm-start destabilizes | Fall back to fresh LoRA init on ASI2/ASI3 if iter-3 step-100 loss > iter-2 step-100 loss + 20%. |
| max_length budget still too tight on ASI1 | Drop the longest 10% of carry-forward rows on ASI1 only; document in manifest. |
| Eval contamination from new tasks | New task ids in Track C.2 are added to `quantum_generalization_holdout_v3_multi_framework.txt` ONLY; they must not be added to any training source JSONL. |

## 8. Out of scope for this track

- Running the GLM5.2 teacher to generate new corrections (needs the eval
  results first; owned by the training-launch session).
- Modifying the LoRA trainer (`training/qwen_sft_peft.py`,
  `training/qwen_sft_peft_kl.py`).
- Modifying the RL-distill pipeline (owned by session-A).

## 9. Files produced by this track

- `docs/iter3-dataset-spec-2026-07-07.md` (this file)
- `scripts/prepare_iter3_distill_sft.py` (scaffold; runs `--check` only)
- `data/generated/glm52_soft_distill_sft_iter3/manifest.json` (stub; rows
  filled in after iter-2 eval)

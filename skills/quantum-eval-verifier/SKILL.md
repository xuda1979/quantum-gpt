---
name: quantum-eval-verifier
description: Use when verifying quantum-coding LLM output — running pass@k evals, executing candidate quantum code in sandboxes, scoring artifacts, comparing base-vs-adapter, or deciding whether an adapter regresses and should gate the RL loop.
---

# Quantum Eval Verifier

Use this skill whenever the task involves *measuring* a quantum-coding model:
running `evals/subsystem/harness.py`, executing candidate code from
`evals/benchmarks/`, scoring with `training/artifact_scoring.py`, comparing
two adapters, or deciding whether an eval result should pause the RL+distill
loop. This is the skill that keeps "did the model actually get better?"
honest.

It is the eval-side counterpart to `lean-software-engineering` (which governs
*how* you engineer) and `huanxin-s3-ops` (which governs *where* artifacts
live). Use it whenever you would otherwise eyeball a result file.

## Core Principles

1. **Run the code, don't read the code.** A candidate quantum program is
   correct only after it has been executed in the sandbox and the test
   harness returned `passed: true`. Never claim a pass from visual inspection.
2. **Same harness, same tasks, same seed.** Compare base vs adapter only on
   the same held-out benchmark with the same `--k`, `--temperature`, and
   `--seed`. Any deviation invalidates the comparison.
3. **Score vectors, not vibes.** When a per-artifact score exists, read the
   full vector (`r_pass`, `r_partial`, `r_runnable`, `r_api_correct`,
   `r_style`, `r_hallucination_penalty`, ...) — a single `pass@1` number
   hides *why*.
4. **Gate on regression, not on noise.** A single eval dip is noise. Two
   consecutive dips on the same held-out set, or one dip beyond the
   configured tolerance, is a regression — pause the loop and raise it.
5. **Never train on the holdout.** The held-out benchmark is read-only for
   the lifetime of the program. If you suspect contamination, stop and
   document it; do not "fix" it by editing the holdout.

## Standard Procedure

### A. Run a pass@k eval

```bash
# Base vs adapter on the held-out quantum benchmark, identical conditions.
python3 evals/subsystem/harness.py \
  --base-model /path/to/base \
  --adapter /path/to/adapter \
  --tasks quantum_generalization_holdout_v1 \
  --models both \
  --k 1 \
  --temperature 0.0 \
  --output evals/runs/<run-name>/eval.json
```

Then summarise:

```bash
python3 evals/subsystem/analyzer.py compare \
  --baseline <baseline-eval.json> \
  --candidate <candidate-eval.json>
```

### B. Execute a single candidate against a task

For ad-hoc verification (no full eval run):

```bash
# task_dir contains task.json (meta + tests). candidate.py is the model output.
python3 - <<'PY'
from pathlib import Path
from evals.subsystem.harness import run_test
import json
task_dir = Path("evals/tasks/<task-id>")
meta = json.loads((task_dir / "task.json").read_text())
code = Path("/tmp/candidate.py").read_text()
result = run_test(task_dir, meta, code, Path("/tmp/candidate.py"))
print(result)  # {'passed': bool, 'details': {...}}
PY
```

### C. Score an artifact (per-artifact rubric)

```python
from training.artifact_scoring import score_artifact
scores = score_artifact(
    teacher_eval_result={...},   # from GLM5.2 teacher eval
    correct_answer="...",
    resample_attempts=1,
)
# scores -> {'r_pass':..., 'r_partial':..., 'r_runnable':..., 'r_api_correct':..., ...}
```

### D. Decide whether to gate the RL loop

Apply this rule *after* a fresh eval is written for the current adapter:

| Signal | Action |
|-------|--------|
| `pass@1` improved or flat vs. previous adapter | continue RL loop |
| `pass@1` dropped < tolerance (default 3% abs) | continue, flag in manifest |
| `pass@1` dropped ≥ tolerance, one eval | pause, rerun eval with new seed |
| `pass@1` dropped ≥ tolerance, two consecutive evals | **hard stop**: write `guardrail_trip: eval_regression`, do not launch next training round |
| `r_runnable` collapsed (>20% abs drop) | hard stop regardless of `pass@1` |

Tolerance and the consecutive-eval rule live in the RL config
(`eval_gate` block); see `scripts/rl_distill_pipeline.py` for the hook.

## Anti-Patterns

- **Cherry-picking tasks.** Do not rerun on a subset after a bad result. The
  held-out benchmark is fixed. If a task is broken, fix the task and version
  the benchmark; do not drop it ad hoc.
- **Comparing across harness versions.** A pass@1 from `run_asi2_35b_pass1_eval.py`
  (legacy) is not comparable to one from `evals/subsystem/harness.py`. Always
  record `schema_version` and harness git SHA in the run card.
- **Trusting teacher self-eval.** GLM5.2 grading the student is a *signal*,
  not ground truth. The ground-truth signal is `run_test` on held-out tasks.
- **Silent re-runs.** If you rerun an eval because the first looked weird,
  record both runs. Do not overwrite the first.

## Files This Skill Touches

- `evals/subsystem/harness.py` — pass@k execution
- `evals/subsystem/analyzer.py` — comparison + trend
- `evals/subsystem/reporter.py` — markdown summaries
- `evals/subsystem/dataset_gap.py` — gap → next-iter recommendations
- `evals/benchmarks/*.txt` — held-out task lists (read-only)
- `evals/runs/<run-name>/eval.json` — run artifacts
- `training/artifact_scoring.py` — per-artifact rubric
- `scripts/rl_distill_pipeline.py` — eval gate hook (reads `eval_gate` config)
- `configs/rl/*.json` — `eval_gate` block

## When To Load References

- This skill is self-contained. If you need deeper context on the rubric,
  read `docs/quantum-coding-reward-rubric-2026-07-07.md`. If you need the
  RL loop mechanics, read `docs/rl-distill-iteration-process-2026-07.md`.

## Success Standard

A successful eval step leaves:

- a written `eval.json` under `evals/runs/<run-name>/` with `schema_version`, harness SHA, and full per-task results;
- a comparison delta (vs. baseline) — either a file or a printed table;
- a clear gate decision: `continue` | `pause-rerun` | `hard-stop`, with the numeric threshold that triggered it.

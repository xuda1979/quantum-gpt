# Local Eval Harness v0

This directory contains the first CPU-feasible evaluation harness for the quantum coding LLM R&D project.

## Purpose

Stand up a tiny but real local evaluation loop that can score model outputs on both:

- quantum coding tasks
- general software-engineering tasks

The v0 harness is intentionally small:

- 19 seed tasks total
- 8 quantum tasks
- 11 software tasks
- local reference tests
- optional generated-candidate evaluation via a simple manifest

This is enough to validate task packaging, scoring, and the first model-facing seam before wiring in inference.

## Layout

```text
evals/
  README.md
  tasks/
    quantum/
      bell_pair_construction/
      circuit_phase_repair/
      gate_alias_normalization/
      measurement_bug_repair/
      qft_phase_pattern/
      superdense_coding/
      stabilizer_tableau_update_repair/
      teleportation_corrections/
    software/
      config_merge/
      docstring_contract/
      duplicate_logic_refactor/
      off_by_one_bugfix/
      parser_regression_tests/
      patch_application_conflict_resolver/
      multifile_patch_conflict_repair/
      session_event_log/
      session_window_summary/
  runner/
    README.md
    run_eval.py
    example-candidate-map.json
```

Each task directory contains:

- `task.json` — metadata and scoring info
- `candidate.py` — a reference candidate solution file
- `tests.py` — executable validation logic

## Current Scope

The runner can now execute either:

- the bundled reference candidates, or
- externally generated candidate files supplied through a JSON task-to-file mapping

That gives the project a reproducible path to score model outputs without changing task packaging.

The harness now also supports a lightweight run-directory workflow for prompt preparation and output capture.
A prepared run bundles the system prompt, per-task prompts, empty candidate output files, a scoring-ready candidate map, and manifest metadata in one place.
Runs can now be materialized under named prompt styles such as `direct`, `plan_then_code`, and `repair_focused` to support apples-to-apples prompt comparisons.

Scored run directories can now emit a `scorecard.json` file automatically, and `evals/runner/compare_runs.py` can summarize multiple scored runs side by side for prompt-style or model comparisons.

The scorer is also crash-tolerant: if a generated candidate is malformed or causes a task test to raise unexpectedly, the runner records a failed task with traceback diagnostics and continues scoring the rest of the batch.

Later phases can add:

- additional workspace-mode repair tasks with multiple writable candidate files
- richer hosted or local inference adapters
- timing metrics
- richer batch metadata

A first generic execution adapter now exists in `evals/runner/execute_run.py`. It can execute a prepared run directory end to end by calling an arbitrary shell command once per task, capturing stdout into the task's candidate file, saving stderr/stdout logs, recording `execution-log.json`, and then scoring the run. This provides a provider-agnostic bridge between prompt preparation and scoring while staying CPU-friendly and standard-library only.

The repo now also includes `evals/runner/mock_model_adapter.py`, which makes the model-execution seam explicit. The current mock backends are intentionally simple, but they define the interface that a real hosted or local inference adapter should satisfy.

## How to run

From the workspace root:

```bash
python3 evals/runner/run_eval.py
python3 evals/runner/run_eval.py --candidate-map evals/runner/example-candidate-map.json
```

## What success means

If all 19 bundled seed tasks pass, the task packaging and scoring loop are working.
If a candidate map is supplied, the same harness can score generated files task-by-task with identical tests.
That gives the project a stable base for future prompt and model comparisons.

# Eval Runner

`run_eval.py` is a minimal local runner for seed-task validation.

## Design

- Reads task metadata from `evals/tasks/**/task.json`
- Executes each task's `tests.py`
- Reports per-task pass/fail
- Emits category and domain summaries
- Uses only Python standard library

## Current contract

Each `tests.py` file must expose:

- `run_tests(candidate_path: str) -> dict`

Returned dictionary format:

```python
{
    "passed": True,
    "details": ["optional diagnostic lines"]
}
```

If a task test crashes or a candidate raises an unexpected import/runtime error, `run_eval.py` now records that task as a normal failed result with traceback details instead of aborting the full batch. This is important for model evaluation because malformed generations should degrade the scorecard, not prevent the rest of the run from being measured.

## Candidate sources

By default, the runner evaluates each task's bundled reference `candidate.py`.

To evaluate generated outputs instead, pass a candidate map JSON file:

```bash
python3 evals/runner/run_eval.py --candidate-map evals/runner/example-candidate-map.json
```

The JSON format is:

```json
{
  "task_id": "path/to/generated_candidate.py"
}
```

Paths may be absolute or relative to the candidate-map file.
Tasks not listed in the map continue using their bundled reference candidates.

## Run directory workflow

To prepare a timestamped eval batch with prompt files and empty candidate output slots:

```bash
python3 evals/runner/prepare_prompts.py
```

Or choose a deterministic directory name and prompt style:

```bash
python3 evals/runner/prepare_prompts.py --run-name manual-smoke-test --prompt-style direct
python3 evals/runner/prepare_prompts.py --run-name manual-plan-test --prompt-style plan_then_code
```

This creates `evals/runs/<run-id>/` containing:

- `SYSTEM_PROMPT.txt` - shared system prompt for the batch
- `prompts/<task_id>.txt` - per-task user prompts built from metadata and tests
- `candidates/<task_id>.py` - empty files where model outputs should be saved
- `candidate-map.json` - ready-to-score mapping for `run_eval.py`
- `manifest.json` - batch metadata for reproducibility, including prompt style and notes
- `README.txt` - local workflow reminder

Once candidate files are filled, score the run with:

```bash
python3 evals/runner/run_eval.py --candidate-map evals/runs/<run-id>/candidate-map.json
```

When `--candidate-map` points at a prepared run directory, the runner also writes `scorecard.json` beside the manifest. That makes each run self-contained: prompts, candidate files, metadata, and scored results live in one folder.

To compare two or more scored runs side by side:

```bash
python3 evals/runner/compare_runs.py evals/runs/style-direct evals/runs/style-plan
```

The comparison report shows backend/model metadata, overall pass rate, domain/category breakdowns, and any failing tasks.

To execute a prepared run in one command, use `execute_run.py` with any shell command that reads the exported env vars and prints the candidate Python file to stdout:

```bash
python3 evals/runner/execute_run.py evals/runs/manual-smoke-test \
  --command 'cat "$EVAL_PROMPT_PATH" > /dev/null; cat "$EVAL_SYSTEM_PROMPT_PATH" > /dev/null; printf "def placeholder():\n    return 0\n"'
```

A cleaner pattern is to route execution through an explicit adapter script. The repo now includes `evals/runner/mock_model_adapter.py`, which defines a stable seam for future real model backends:

```bash
python3 evals/runner/execute_run.py evals/runs/manual-smoke-test \
  --command 'python3 evals/runner/mock_model_adapter.py --backend reference-copy --task-id "$EVAL_TASK_ID"'
```

Today that adapter supports:

- `reference-copy` — emits the task's bundled reference candidate (useful for end-to-end smoke tests)
- `echo-prompt` — emits the prompt itself (useful for log/debug validation)

There is now also a real hosted backend at `evals/runner/openai_model_adapter.py`:

```bash
python3 evals/runner/execute_run.py evals/runs/openai-baseline-smoke \
  --command 'python3 evals/runner/openai_model_adapter.py'
```

The adapter reads `EVAL_SYSTEM_PROMPT_PATH` and `EVAL_PROMPT_PATH`, calls the OpenAI Responses API, prints candidate code to stdout, and writes provider/model token metadata to stderr for per-task logs. By default it targets `gpt-5.4`, with optional overrides via `--model`, `--api-base`, `--max-output-tokens`, and `--reasoning-effort`.

The point is not the mock backend itself. The point is to make the model-adapter boundary explicit so later OpenAI/OpenClaw or local-runtime backends can be dropped in without changing run packaging.

Per-task env vars include:

- `EVAL_SYSTEM_PROMPT_PATH`
- `EVAL_PROMPT_PATH`
- `EVAL_CANDIDATE_PATH`
- `EVAL_TASK_ID`
- `EVAL_TASK_NAME`
- `EVAL_TASK_DOMAIN`
- `EVAL_TASK_CATEGORY`
- `EVAL_PROMPT_STYLE`
- `EVAL_PROMPT_VERSION`

The command runs once per task. Its stdout is captured to `candidates/<task_id>.py`, stderr is saved under `logs/`, `execution-log.json` records return codes and byte counts, and the run is scored automatically unless `--no-score` is passed.

If you want run artifacts to be self-describing, `execute_run.py` can now also stamp backend metadata into both `manifest.json` and `execution-log.json`:

```bash
python3 evals/runner/execute_run.py evals/runs/openai-baseline-smoke \
  --command 'python3 evals/runner/openai_model_adapter.py' \
  --backend-name openai \
  --backend-model gpt-5.4 \
  --backend-settings-json '{"reasoning_effort":"medium","max_output_tokens":1600}'
```

That keeps provider/model/decoding settings beside the scorecard instead of burying them only in per-task stderr logs.

`run_eval.py` now snapshots that backend metadata into `scorecard.json`, and `compare_runs.py` prints it directly, so cross-backend comparisons can be read from scorecards alone.

This keeps the harness provider-agnostic: later adapters can wrap local inference, an ACP harness, or an API client without changing task packaging or scoring.

Recommended comparison pattern:

- prepare one run with `--prompt-style direct`
- prepare another with `--prompt-style plan_then_code`
- keep task set identical
- record any model/provider details in `--notes`
- compare pass rates on the same scorer

The current seed set now spans 19 tasks total: 8 quantum and 11 software. The newer tasks stay intentionally small and deterministic, but they now extend beyond single-file puzzles into stacked-constraint repairs, the first tiny contract-preserving multi-file repair task, a first true workspace-bound repair task (`software_workspace_patch_bundle_repair`), and a workspace-mode smoke task that validates multi-file candidate scoring support, alongside exact QFT phase generation, teleportation correction logic, noisy-gate-stream phase repair, gate-alias normalization, recursive config merges, docstring-level API contracts, and stateful session bookkeeping.

## Workspace-mode task contract

The runner now supports an optional workspace-mode task format for true multi-file repair tasks.

Add these fields to `task.json`:

```json
{
  "candidate_files": ["pkg/module_a.py", "pkg/module_b.py"],
  "workspace_dir": "workspace",
  "test_file": "tests.py"
}
```

Meaning:

- `workspace_dir` points to a bundled support subtree copied into a temp directory during scoring
- `candidate_files` lists writable relative paths that are overlaid onto that temp workspace before tests run
- tests may expose `run_tests(workspace_root: str) -> dict`
- if `candidate_files` is absent, the old single-file `candidate_file` path still works unchanged

This is the smallest runner extension needed to support genuinely coupled multi-file repair tasks while preserving backward compatibility for the older single-file harness.

## Why this design

It keeps the first version simple and CPU-cheap while leaving room for later support for:

- generated candidates
- prompt-mode comparisons
- model output capture directories
- timing metrics
- richer diagnostics

# Real Model Backend Plan

## Goal

Replace the current mock prepared-run adapter with a real model-execution backend that can:

1. read `SYSTEM_PROMPT.txt` and per-task prompt files from a prepared run,
2. call an actual model,
3. write raw candidate code to stdout for `execute_run.py`,
4. preserve reproducibility metadata for later scorecard comparison.

This note defines the smallest practical path under the current workspace constraints.

## Current State

Already working:

- prepared run generation via `evals/runner/prepare_prompts.py`
- task-by-task execution via `evals/runner/execute_run.py`
- crash-tolerant scoring via `evals/runner/run_eval.py`
- score persistence and run comparison
- explicit adapter seam via `evals/runner/mock_model_adapter.py`

Missing:

- a backend that actually queries a model instead of copying references or echoing prompts

## Constraints

- CPU-first local workflow
- orchestration model should use OpenAI GPT-5.4 API
- keep the adapter boundary simple and provider-agnostic
- avoid redesigning task packaging
- prefer narrow, testable steps over all-at-once integration

## Recommended Adapter Contract

A real adapter should keep the same high-level behavior as the mock adapter:

- input:
  - task id
  - system prompt path
  - user prompt path
  - optional metadata such as prompt style and run directory
- output:
  - final candidate file contents on stdout only
- side effects:
  - none beyond normal stderr diagnostics

That keeps `execute_run.py` unchanged and allows multiple backends to coexist.

## Smallest Practical Backend Sequence

### Phase 1: OpenAI-backed adapter

Implement a script such as `evals/runner/openai_model_adapter.py` that:

- reads the system prompt and task prompt from files
- calls the OpenAI Responses API with `gpt-5.4`
- requests plain code output only
- prints the returned text to stdout
- records provider/model metadata on stderr for logs if useful

Why first:

- matches the current orchestration preference
- easiest path to the first genuine baseline run
- avoids waiting on local quantized Qwen inference stack decisions

### Phase 2: Local Qwen runtime adapter

After the OpenAI-backed baseline exists, add a second backend for local Qwen inference. Candidate runtime options to evaluate later:

- llama.cpp-compatible quantized path
- MLX if the target checkpoint/runtime combination is practical on this machine
- another lightweight local inference wrapper if it can be scripted cleanly

Why second:

- local runtime selection is still an open research question
- adapter interface should stabilize first

## Reproducibility Requirements

For each real backend run, persist enough metadata to compare later:

- provider/backend name
- model identifier
- run id
- prompt style and prompt version
- execution timestamp
- any decoding settings that materially affect outputs

These fields should live in the prepared run artifacts themselves, not only in stderr logs. The current runner now stamps backend metadata into `manifest.json`, `execution-log.json`, and `scorecard.json`, which is enough for the first hosted baselines and for self-describing run comparisons.

## Risks

### Output contamination

Model may emit markdown fences or commentary instead of raw code.

Mitigation:

- keep prompts strict
- add a minimal post-processing/sanitization step only if necessary, and document it clearly

### Timeout/latency variability

Hosted calls may be much slower than mock/reference backends.

Mitigation:

- start with the 6-task seed suite only
- preserve per-task execution logs
- keep task-level timeout control in `execute_run.py`

### False progress from a strong hosted model

A GPT-5.4 baseline is useful for validating the infrastructure, but it is not the same thing as demonstrating target-model readiness.

Mitigation:

- label results clearly as hosted-orchestration baselines
- use them to calibrate task quality and scoring sensitivity, not as proof that the Qwen target is solved

## Status Update

Phase 1 is now implemented as `evals/runner/openai_model_adapter.py`.

The adapter:

- reads `SYSTEM_PROMPT.txt` and per-task prompt files through the prepared-run env contract,
- calls the OpenAI Responses API,
- prints plain candidate text to stdout for `execute_run.py`,
- strips simple markdown code fences by default,
- emits provider/model/usage metadata to stderr so prepared runs retain per-task execution traces.

## Remaining Immediate Work

1. generate one genuine baseline run and scorecard,
2. inspect failures for prompt or sanitization issues,
3. update the paper with a short empirical section describing that first result honestly.

That remains the highest-leverage path from infrastructure work to actual model evaluation.

## Artifact Hygiene Note

Run-comparison tooling should surface backend metadata directly from durable artifacts rather than forcing manual manifest inspection. The runner now stamps backend metadata into the run manifest at execution time, and scorecards should carry a snapshot of that metadata so later comparisons remain interpretable even if manifests move or downstream tooling reads only `scorecard.json`.

# Eval Difficulty Jump v2

## Why this note exists

`software_multifile_patch_conflict_repair` was the right experiment to run next, and it taught something useful. The hosted baseline (`openai/gpt-5.4`) still passed cleanly on the 17-task harness, including the new `multifile_repair` category.

That result does **not** mean the direction was wrong. It means the first version of the direction was still too weak.

The task added a cross-module-style contract, but the effective candidate surface remained a single generated entrypoint (`candidate.py`) with all required behavior visible to the model and all important invariants made explicit by tests. A strong hosted model can still brute-force that format by generating one internally consistent implementation from scratch.

So this note tightens the target. It distinguishes between "single-entrypoint multi-contract" tasks and truly coupled multi-file repair tasks, then defines the smallest eval-format change needed to support the latter without making the harness heavyweight.

## New distinction

### Level A: single-entrypoint multi-contract tasks

Properties:

- tests check more than one behavior contract
- contracts may reflect a notional multi-module design
- candidate still consists of one generated file
- model can satisfy the benchmark with a clean rewrite that reimplements everything locally

Example:

- `software_multifile_patch_conflict_repair`

These tasks are still useful. They are sharper than simple single-function puzzles. They test whether a model can keep several constraints aligned at once.

But they do **not** yet force the model to preserve real structure across files.

### Level B: truly coupled multi-file repair tasks

Properties:

- the candidate surface contains multiple files
- at least one file is pre-existing support code that should remain intact or near-intact
- correctness depends on preserving contracts across file boundaries
- tests import through public module boundaries, not only a fused candidate entrypoint
- naive "rewrite everything in one place" behavior is either impossible or punished

This is the actual target for the next difficulty jump.

## Why level B matters

The project does not mainly need harder logic puzzles. It needs benchmark pressure that resembles real software maintenance:

- preserve interfaces while changing behavior
- modify one layer without breaking another
- keep schemas and summaries stable
- respect hidden coupling between engine logic and presentation/helpers
- avoid replacing a repair task with a greenfield rewrite

That is closer to the retention problem we actually care about for a quantum coding model with strong software-engineering behavior.

## Smallest viable eval-format change

Do **not** redesign the whole harness.

The smallest useful extension is:

1. allow a task to declare a small `workspace/` subtree of support files
2. copy that subtree into a per-task temp directory during scoring
3. overlay model-generated outputs onto one or more declared writable candidate paths
4. run the task tests against that temp workspace

This is enough to create real multi-file repair pressure while keeping the current runner model mostly intact.

## Proposed task metadata extension

Current tasks assume a single `candidate_file`.

Add optional fields like:

```json
{
  "candidate_files": [
    "candidate/module_a.py",
    "candidate/module_b.py"
  ],
  "workspace_dir": "workspace",
  "entry_test_mode": "workspace"
}
```

Meaning:

- `workspace_dir` contains fixed support files bundled with the task
- `candidate_files` are the files the model is allowed to generate/replace
- tests should run with the temp workspace root on `sys.path`
- if `candidate_files` is absent, runner behavior stays exactly as it is now

This keeps backward compatibility for the current 17 tasks.

## Scoring behavior change

For workspace-mode tasks:

1. create temp dir
2. copy `workspace/` into temp dir
3. copy generated candidate files into the declared relative paths
4. execute `tests.py` against that temp workspace
5. clean up temp dir after scoring

This is still CPU-cheap and standard-library friendly.

## Guardrails for the new task family

To avoid accidental benchmark bloat, keep these constraints:

- max 2-4 writable candidate files per task
- max total task workspace size in the low KB range
- no third-party dependencies
- tests must still finish quickly on CPU
- at least one public interface boundary must matter
- at least one naive rewrite path should be meaningfully punished

## Recommended first true level-B task

### `software_workspace_patch_bundle_repair`

Shape:

- `workspace/models.py`
- `workspace/patch_engine.py`
- `workspace/reporting.py`
- generated candidate file(s): likely only `patch_engine.py` or `patch_engine.py` plus one helper

Core pressure:

- engine and reporting must agree on conflict schema and ordering
- support models remain shared across modules
- tests import through module boundaries
- changing the wrong file shape breaks reporting
- rewriting logic into one file is no longer the easy escape hatch

This is a better next step than adding a quantum companion immediately because it validates the format extension itself with the simplest domain first.

## What not to do next

- do not convert all existing tasks to workspace mode
- do not add many new tasks before the runner extension works
- do not make candidate surfaces large
- do not rely on prose-only patch-locality requests; encode locality in file boundaries and tests

## Success criterion for v2

The v2 jump is successful if any one of these happens:

1. the hosted baseline records its first meaningful failure on a true workspace-mode task
2. the hosted baseline still passes, but only by respecting real file boundaries
3. the runner can support mixed single-file and workspace-mode tasks without breaking old experiments

That is enough. The immediate goal is not benchmark size. It is benchmark shape.

## Decision

The next eval-infrastructure change should be a **minimal workspace-mode extension** to the runner, followed by exactly one true multi-file repair task built on top of it.

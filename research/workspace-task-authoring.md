# Workspace-Mode Task Authoring Notes

## Why this note exists

The runner now supports workspace-mode tasks, but the authoring contract was still under-documented at the task-creation level. The first real workspace task (`software_workspace_patch_bundle_repair`) exposed the practical rules clearly enough to write them down.

This note captures the smallest set of authoring rules that keep workspace tasks reproducible, reference-scoreable, and hard to accidentally mispackage.

## Minimal task shape

A workspace-mode task should contain:

- `task.json`
- `tests.py`
- `workspace/` with fixed support files
- one or more writable reference candidate files at task root matching `candidate_files`

Example:

```text
evals/tasks/software/example_workspace_task/
  task.json
  tests.py
  workspace/
    pkg/
      __init__.py
      models.py
      reporting.py
  pkg/
    patch_engine.py
```

## Required metadata

Use `candidate_files`, not `candidate_file`:

```json
{
  "id": "software_example_workspace_task",
  "name": "Example workspace task",
  "domain": "software",
  "category": "workspace_repair",
  "candidate_files": ["pkg/patch_engine.py"],
  "workspace_dir": "workspace",
  "test_file": "tests.py"
}
```

## Important packaging rule

The writable reference candidate must exist at the task root using the same relative path declared in `candidate_files`.

For example, if `candidate_files` includes `pkg/patch_engine.py`, then this file must exist:

- `evals/tasks/.../pkg/patch_engine.py`

and not only this file:

- `evals/tasks/.../workspace/pkg/patch_engine.py`

Why:

- the runner copies `workspace/` into a temp directory
- then overlays candidate files from either the task-root reference path or an override directory
- reference scoring fails before real task logic runs if the task-root writable file is missing

This is easy to miss because support code and writable code often start identical during task creation.

## Test contract guidance

Prefer:

```python
def run_tests(workspace_root: str) -> dict:
    ...
```

Tests should:

- import through public module boundaries from the temp workspace
- check that inputs are not mutated when relevant
- verify both engine semantics and downstream reporting/schema contracts when that coupling matters
- clear imported modules from `sys.modules` before returning so repeated task execution stays clean

## Design guidance

A good workspace-mode task should make file boundaries matter.

Useful pressure patterns:

- one writable logic file plus one fixed reporting/schema module
- hidden coupling through shared helper/model functions
- preserving one contract while changing another behavior path
- imports that punish rewriting everything into a single generated file

Avoid:

- large workspaces
- candidate surfaces bigger than 2-4 files
- tasks where support modules are irrelevant to correctness
- prose-only requests for locality without any file-boundary enforcement in tests

## Validation checklist

Before claiming a workspace task is ready:

1. `python3 evals/runner/run_eval.py` passes locally
2. the task passes when scored through the normal reference path
3. the task-root writable candidate file exists for every relative path in `candidate_files`
4. tests import from the copied temp workspace, not from the repo root by accident
5. repeated runs do not leak modules through `sys.modules`

## What I learned

The hard part was not runner code. It was task packaging discipline. Without an explicit note, future workspace tasks are likely to repeat the same mistake: placing the writable reference file only under `workspace/` and forgetting that the overlay path comes from task root during reference scoring.

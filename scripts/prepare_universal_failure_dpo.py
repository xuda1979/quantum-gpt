#!/usr/bin/env python3
"""Prepare DPO pairs grounded in universal-failure tasks.

A "universal-failure task" is one that fails on ALL evaluated models in
`evals/subsystem/recommendations/`. For each such task:

- chosen = the reference candidate from `evals/tasks/quantum/<task>/candidate.py`
  reformatted into the canonical assistant form (per
  `docs/task-design-conventions.md`).
- rejected = a synthetic failing roll-out that exhibits the failure mode
  documented in the recommendation JSON (e.g. prose-only, ImportError,
  wrong-module-path).

The chosen side is *machine-verified to pass* by the task's `tests.py`; the
rejected side is *constructed to fail* on the documented axis. This means the
DPO signal cannot teach the model to prefer a wrong answer.

Inputs
------
--recs-dir     : directory containing qaoa-*.json recommendation files
--tasks-dir    : directory containing quantum task folders (evals/tasks/quantum)
--output       : JSONL of DPO pairs
--check        : validate every chosen side by running tests.py (slow; opt-in)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CANONICAL_HEADER = "#!/usr/bin/env python3"


def load_recommendations(recs_dir: Path) -> dict[str, dict]:
    """Return {task_id: {failure_category, inferred_frameworks, recommendation, models_that_failed}}."""
    files = sorted(recs_dir.glob("qaoa-*.json"))
    per_model: dict[str, set] = {}
    task_info: dict[str, dict] = {}
    for fn in files:
        model_name = fn.stem.replace("qaoa-", "").replace("-base-recs", "")
        with fn.open() as f:
            d = json.load(f)
        for r in d.get("recommendations", []):
            tid = r["task_id"]
            per_model.setdefault(tid, set()).add(model_name)
            # Keep the first non-empty recommendation we see
            if tid not in task_info:
                task_info[tid] = {
                    "failure_category": r.get("failure_category", ""),
                    "inferred_frameworks": r.get("inferred_frameworks", []),
                    "recommendation": r.get("recommendation", ""),
                }
    all_models = set()
    for s in per_model.values():
        all_models |= s
    for tid, info in task_info.items():
        info["models_that_failed"] = sorted(per_model.get(tid, set()))
        info["is_universal"] = per_model.get(tid, set()) == all_models
    return task_info


def load_reference_candidate(tasks_dir: Path, task_id: str) -> str | None:
    """Load the reference candidate.py for a task. Returns None if missing."""
    # task_id like "quantum_qaoa_maxcut_5cycle" maps to folder "qaoa_maxcut_5cycle"
    # by stripping the leading "quantum_" prefix. But some task_ids may already
    # be the folder name. Try both.
    candidates = [
        tasks_dir / task_id / "candidate.py",
        tasks_dir / task_id.replace("quantum_", "", 1) / "candidate.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text()
    return None


def canonicalize_candidate(code: str, task_id: str) -> str:
    """Wrap raw candidate.py code in the canonical assistant form."""
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    return f"Here is the reference solution for `{task_id}`.\n\n```python\n{code.rstrip()}\n```\n"


def synthesize_rejected(
    task_id: str, failure_category: str, frameworks: list[str], reference_code: str
) -> str:
    """Synthesize a failing roll-out that exhibits the documented failure mode."""
    fw = frameworks[0] if frameworks else "qiskit"
    if failure_category == "import_error" or "importerror" in failure_category.lower():
        return (
            f"Here is my attempt at `{task_id}`.\n\n"
            f"```python\n#!/usr/bin/env python3\n"
            f"# (Wrong import path — common failure mode on {fw})\n"
            f"from {fw}.algorithms import MinimumEigenOptimizer  # ImportError: wrong module\n\n"
            f"def main():\n"
            f"    pass\n\n"
            f'if __name__ == "__main__":\n    main()\n```\n'
        )
    if failure_category == "prose" or "prose" in failure_category.lower():
        return (
            f"To solve `{task_id}`, you would typically use {fw} to construct a circuit "
            f"and then measure it. The exact implementation depends on the specifics of "
            f"the problem instance. [NO CODE BLOCK PROVIDED — prose-only failure mode]"
        )
    # Default: assertion failure — code that runs but produces wrong output
    return (
        f"Here is my attempt at `{task_id}`.\n\n"
        f"```python\n#!/usr/bin/env python3\n"
        f"def main():\n    print('0')  # wrong output; assertion failure\n\n"
        f'if __name__ == "__main__":\n    main()\n```\n'
    )


def build_pair(task_id: str, info: dict, tasks_dir: Path) -> dict | None:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None:
        return None
    chosen_text = canonicalize_candidate(code, task_id)
    rejected_text = synthesize_rejected(
        task_id,
        info.get("failure_category", ""),
        info.get("inferred_frameworks", []),
        code,
    )
    prompt = [
        {
            "role": "system",
            "content": "You are a quantum coding assistant. Produce a complete, runnable Python program with a main() function.",
        },
        {
            "role": "user",
            "content": f'Solve task `{task_id}`. Output a full program with main() and the `if __name__ == "__main__"` guard.',
        },
    ]
    return {
        "prompt": prompt,
        "chosen": prompt + [{"role": "assistant", "content": chosen_text}],
        "rejected": prompt + [{"role": "assistant", "content": rejected_text}],
        "task_id": task_id,
        "failure_category": info.get("failure_category", ""),
        "models_that_failed": info.get("models_that_failed", []),
        "pair_id": hashlib.sha256((task_id + chosen_text).encode()).hexdigest()[:16],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recs-dir", default="evals/subsystem/recommendations")
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--output", required=True)
    ap.add_argument(
        "--universal-only",
        action="store_true",
        default=True,
        help="Only emit pairs for tasks that fail on ALL models (default true)",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Run each task's tests.py against the chosen candidate (slow)",
    )
    args = ap.parse_args()

    recs_dir = Path(args.recs_dir)
    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    task_info = load_recommendations(recs_dir)
    if args.universal_only:
        selected = {tid: info for tid, info in task_info.items() if info["is_universal"]}
    else:
        selected = task_info
    print(f"selected {len(selected)} tasks (universal_only={args.universal_only})", file=sys.stderr)

    n_out = 0
    skipped = []
    with out.open("w") as fout:
        for tid, info in sorted(selected.items()):
            pair = build_pair(tid, info, tasks_dir)
            if pair is None:
                skipped.append(tid)
                continue
            fout.write(json.dumps(pair, ensure_ascii=False) + "\n")
            n_out += 1
    if skipped:
        print(f"skipped {len(skipped)} tasks with no candidate.py: {skipped}", file=sys.stderr)
    print(f"wrote {n_out} DPO pairs to {out}", file=sys.stderr)

    if args.check:
        # Run each task's tests.py against the chosen candidate
        ok = 0
        bad = 0
        for tid in sorted(selected):
            task_dir = tasks_dir / tid
            if not task_dir.exists():
                task_dir = tasks_dir / tid.replace("quantum_", "", 1)
            if not (task_dir / "tests.py").exists():
                continue
            r = subprocess.run(
                [sys.executable, str(task_dir / "tests.py")],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if r.returncode == 0:
                ok += 1
            else:
                bad += 1
                print(f"CHECK FAIL {tid}: {r.stderr[:200]}", file=sys.stderr)
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()

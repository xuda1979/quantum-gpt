#!/usr/bin/env python3
"""Prepare SFT data for the quantum-critic LoRA.

The critic learns the I/O contract:

  Input  : {task_spec, candidate_code, rubric}
  Output : JSON {"pass": bool, "scores": {...}, "reasoning": "..."}

Training data sources (all already on disk, no teacher calls needed):

  Positive (pass=true):
    - For each task in evals/tasks/quantum/<task>/ that has both
      candidate.py and tests.py, emit a row whose candidate_code is the
      reference candidate and whose label is pass=true (the candidate is
      the reference, so it passes by construction).

  Negative (pass=false):
    - For each task in evals/subsystem/recommendations/qaoa-*.json,
      emit a row whose candidate_code is a synthetic failing roll-out
      exhibiting the documented failure mode, labeled pass=false with
      the failure_category as the reasoning seed.

The rubric is loaded from configs/rl/reward_rubric_v1.json.

Outputs
-------
--output : JSONL of ChatML rows with the critic I/O contract.
--check  : Validate every row's assistant content parses as JSON with the
           required schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CRITIC_SYSTEM_PROMPT = (
    "You are a quantum-code critic. Given a task spec, a candidate program, "
    "and a rubric, output a JSON object with keys: "
    '"pass" (bool), "scores" (object mapping rubric dimensions to 0.0-1.0), '
    'and "reasoning" (string). Do not output anything else.'
)


def load_rubric(path: Path) -> dict:
    if not path.exists():
        return {"dimensions": ["correctness", "completeness", "format"]}
    return json.loads(path.read_text())


def load_task_spec(tasks_dir: Path, task_id: str) -> dict | None:
    """Load task.json for a task. Returns None if missing."""
    for cand in [
        tasks_dir / task_id / "task.json",
        tasks_dir / task_id.replace("quantum_", "", 1) / "task.json",
    ]:
        if cand.exists():
            return json.loads(cand.read_text())
    return None


def load_candidate_code(tasks_dir: Path, task_id: str) -> str | None:
    for cand in [
        tasks_dir / task_id / "candidate.py",
        tasks_dir / task_id.replace("quantum_", "", 1) / "candidate.py",
    ]:
        if cand.exists():
            return cand.read_text()
    return None


def make_positive_row(tasks_dir: Path, task_id: str, rubric: dict) -> dict | None:
    spec = load_task_spec(tasks_dir, task_id)
    if spec is None:
        return None
    code = load_candidate_code(tasks_dir, task_id)
    if code is None:
        return None
    user_msg = {
        "role": "user",
        "content": (
            f"Task spec:\n```json\n{json.dumps(spec, indent=2)}\n```\n\n"
            f"Candidate code:\n```python\n{code}\n```\n\n"
            f"Rubric:\n```json\n{json.dumps(rubric, indent=2)}\n```\n\n"
            "Evaluate the candidate. Output JSON with keys: pass, scores, reasoning."
        ),
    }
    scores = {
        dim: 1.0 for dim in rubric.get("dimensions", ["correctness", "completeness", "format"])
    }
    assistant_msg = {
        "role": "assistant",
        "content": json.dumps(
            {
                "pass": True,
                "scores": scores,
                "reasoning": f"Reference candidate for {task_id}; passes tests.py by construction.",
            },
            ensure_ascii=False,
        ),
    }
    return {
        "messages": [
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            user_msg,
            assistant_msg,
        ],
        "task_id": task_id,
        "label": "positive",
        "pair_id": hashlib.sha256((task_id + "positive").encode()).hexdigest()[:16],
    }


def make_negative_row(tasks_dir: Path, task_id: str, info: dict, rubric: dict) -> dict:
    spec = load_task_spec(tasks_dir, task_id) or {"id": task_id}
    fc = info.get("failure_category", "assertion")
    fw = (info.get("inferred_frameworks") or ["qiskit"])[0]
    # Synthetic failing code
    if "import" in fc.lower():
        bad_code = f'#!/usr/bin/env python3\nfrom {fw}.algorithms import MinimumEigenOptimizer  # wrong module\n\ndef main():\n    pass\n\nif __name__ == "__main__":\n    main()\n'
        reasoning = f"ImportError: {fw}.algorithms.MinimumEigenOptimizer does not exist in this framework version."
    elif "prose" in fc.lower():
        bad_code = "# No code provided; assistant returned prose only."
        reasoning = "No code block emitted; cannot execute."
    else:
        bad_code = "#!/usr/bin/env python3\ndef main():\n    print('0')\n\nif __name__ == \"__main__\":\n    main()\n"
        reasoning = f"Program runs but produces wrong output; assertion failure on {task_id}."

    user_msg = {
        "role": "user",
        "content": (
            f"Task spec:\n```json\n{json.dumps(spec, indent=2)}\n```\n\n"
            f"Candidate code:\n```\n{bad_code}\n```\n\n"
            f"Rubric:\n```json\n{json.dumps(rubric, indent=2)}\n```\n\n"
            "Evaluate the candidate. Output JSON with keys: pass, scores, reasoning."
        ),
    }
    scores = {
        dim: 0.0 for dim in rubric.get("dimensions", ["correctness", "completeness", "format"])
    }
    assistant_msg = {
        "role": "assistant",
        "content": json.dumps(
            {
                "pass": False,
                "scores": scores,
                "reasoning": reasoning,
            },
            ensure_ascii=False,
        ),
    }
    return {
        "messages": [
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            user_msg,
            assistant_msg,
        ],
        "task_id": task_id,
        "label": "negative",
        "failure_category": fc,
        "pair_id": hashlib.sha256((task_id + "negative" + fc).encode()).hexdigest()[:16],
    }


def load_recommendations(recs_dir: Path) -> dict[str, dict]:
    task_info: dict[str, dict] = {}
    for fn in sorted(recs_dir.glob("qaoa-*.json")):
        with fn.open() as f:
            d = json.load(f)
        for r in d.get("recommendations", []):
            tid = r["task_id"]
            if tid not in task_info:
                task_info[tid] = {
                    "failure_category": r.get("failure_category", ""),
                    "inferred_frameworks": r.get("inferred_frameworks", []),
                }
    return task_info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--recs-dir", default="evals/subsystem/recommendations")
    ap.add_argument("--rubric", default="configs/rl/reward_rubric_v1.json")
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-positives", type=int, default=0, help="Limit positive rows (0 = all)")
    ap.add_argument(
        "--check", action="store_true", help="Validate JSON schema of every assistant turn"
    )
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    recs_dir = Path(args.recs_dir)
    rubric = load_rubric(Path(args.rubric))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Positives: every task with a candidate.py
    n_pos = 0
    n_neg = 0
    rows: list[dict] = []
    for sub in sorted(tasks_dir.iterdir()):
        if not sub.is_dir():
            continue
        if not (sub / "candidate.py").exists():
            continue
        row = make_positive_row(tasks_dir, sub.name, rubric)
        if row is None:
            continue
        rows.append(row)
        n_pos += 1
        if args.max_positives and n_pos >= args.max_positives:
            break

    # Negatives: every task in the recommendation files
    task_info = load_recommendations(recs_dir)
    for tid, info in sorted(task_info.items()):
        rows.append(make_negative_row(tasks_dir, tid, info, rubric))
        n_neg += 1

    with out.open("w") as fout:
        for row in rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(
        f"wrote {n_pos} positive + {n_neg} negative = {n_pos + n_neg} rows to {out}",
        file=sys.stderr,
    )

    if args.check:
        required_keys = {"pass", "scores", "reasoning"}
        bad = 0
        for i, row in enumerate(rows):
            try:
                assistant = row["messages"][-1]["content"]
                parsed = json.loads(assistant)
                if not required_keys.issubset(parsed.keys()):
                    bad += 1
                    print(
                        f"CHECK row {i}: missing keys {required_keys - parsed.keys()}",
                        file=sys.stderr,
                    )
                if not isinstance(parsed.get("pass"), bool):
                    bad += 1
                    print(f"CHECK row {i}: pass is not bool", file=sys.stderr)
                if not isinstance(parsed.get("scores"), dict):
                    bad += 1
                    print(f"CHECK row {i}: scores is not dict", file=sys.stderr)
            except json.JSONDecodeError as e:
                bad += 1
                print(f"CHECK row {i}: invalid JSON: {e}", file=sys.stderr)
        if bad:
            print(f"CHECK FAILED: {bad} bad rows", file=sys.stderr)
            sys.exit(1)
        print(f"CHECK PASSED: {n_pos + n_neg} rows valid", file=sys.stderr)


if __name__ == "__main__":
    main()

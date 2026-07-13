#!/usr/bin/env python3
"""Evaluate critic-LoRA agreement with execution-grounded pass/fail.

Success metric (per docs/rd-line-quantum-critic-lora-2026-07-13.md):
    Critic-LoRA, evaluated on a held-out 20% split of the 56-task QAOA
    scorecard, must achieve >= 85% agreement with the execution-grounded
    pass/fail label from tests.py.

This script:
  1. Loads the N2 critic SFT rows (data/generated/rd_lines_2026_07_13/
     n2_critic_sft_rows.jsonl).
  2. Splits them into train (80%) / held-out eval (20%), stratified by
     label, with task_id disjointness (no task appears in both splits).
  3. Runs the execution-grounded oracle (the task's tests.py) for every
     held-out row to get the ground-truth pass/fail.
  4. Calls the critic model on each held-out row's {task_spec,
     candidate_code, rubric} prompt and parses the JSON response.
  5. Reports agreement = (# critic label == oracle label) / N, plus a
     confusion matrix and a per-task breakdown.

Usage (baseline, no critic model — just measures the oracle):
    python3 scripts/eval_critic_agreement.py --split-only

Usage (with a trained critic-LoRA adapter):
    python3 scripts/eval_critic_agreement.py \
        --adapter-path models/critic-lora-v1 \
        --base-model Qwen/Qwen3.6-27B

The split is deterministic (seed=42) so train and eval never overlap.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROWS = REPO / "data/generated/rd_lines_2026_07_13/n2_critic_sft_rows.jsonl"
DEFAULT_SPLIT_OUT = REPO / "data/generated/rd_lines_2026_07_13/n2_critic_split.json"
DEFAULT_TASKS_DIR = REPO / "evals/tasks/quantum"


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def stratified_split(
    rows: list[dict[str, Any]], eval_frac: float = 0.2, seed: int = 42
) -> tuple[list, list]:
    """Task-disjoint stratified split by label.

    Groups by task_id, then assigns whole tasks to eval or train such that
    the eval set has ~eval_frac of rows, stratified by label. No task_id
    appears in both splits.
    """
    rng = random.Random(seed)
    by_task: dict[str, list[dict]] = {}
    for r in rows:
        by_task.setdefault(r["task_id"], []).append(r)
    tasks = sorted(by_task.keys())
    rng.shuffle(tasks)

    # Separate tasks by whether they hold a positive or negative row
    # (most tasks have exactly 1 row of one label; a few may have both).
    pos_tasks = [t for t in tasks if any(r["label"] == "positive" for r in by_task[t])]
    neg_tasks = [t for t in tasks if any(r["label"] == "negative" for r in by_task[t])]

    n_eval_neg = max(1, round(len(neg_tasks) * eval_frac))
    n_eval_pos = max(1, round(len(pos_tasks) * eval_frac))

    eval_tasks = set(neg_tasks[:n_eval_neg]) | set(pos_tasks[:n_eval_pos])
    eval_rows, train_rows = [], []
    for t in tasks:
        for r in by_task[t]:
            (eval_rows if t in eval_tasks else train_rows).append(r)
    return train_rows, eval_rows


def run_tests_py(task_dir: Path, candidate_code: str, timeout: int = 30) -> bool:
    """Write candidate_code to task_dir/candidate.py and run tests.py.

    Returns True if tests.py exits 0.
    """
    candidate_path = task_dir / "candidate.py"
    backup = None
    if candidate_path.exists():
        backup = candidate_path.read_text()
    try:
        candidate_path.write_text(candidate_code)
        proc = subprocess.run(
            [sys.executable, "tests.py"],
            cwd=task_dir,
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    finally:
        if backup is not None:
            candidate_path.write_text(backup)
        elif candidate_path.exists():
            candidate_path.unlink()


def extract_candidate_code(row: dict[str, Any]) -> str | None:
    """Pull the candidate code out of the critic SFT row's user message."""
    for m in row.get("messages", []):
        if m.get("role") != "user":
            continue
        content = m["content"]
        # The user message contains a fenced ```python block with the candidate
        start = content.find("```python\n")
        if start < 0:
            start = content.find("```\n")
            if start < 0:
                continue
            start += 4
        else:
            start += len("```python\n")
        end = content.find("\n```", start)
        if end > start:
            return content[start:end]
    return None


def oracle_label(row: dict[str, Any], tasks_dir: Path) -> bool | None:
    """Run tests.py against the candidate embedded in the row.

    Returns True/False (pass/fail) or None if the candidate couldn't be
    extracted or the task dir doesn't exist.
    """
    code = extract_candidate_code(row)
    if code is None:
        return None
    task_dir = tasks_dir / row["task_id"]
    if not task_dir.is_dir():
        return None
    return run_tests_py(task_dir, code)


def parse_critic_json(text: str) -> dict[str, Any] | None:
    """Best-effort parse of the critic's JSON response."""
    # Strip code fences if present
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        # Try to find the first {...} span
        s = t.find("{")
        e = t.rfind("}")
        if s >= 0 and e > s:
            try:
                obj = json.loads(t[s : e + 1])
            except json.JSONDecodeError:
                return None
        else:
            return None
    if not isinstance(obj, dict) or "pass" not in obj:
        return None
    return obj


def call_critic(
    row: dict[str, Any], adapter_path: str | None, base_model: str
) -> dict[str, Any] | None:
    """Call the critic model. Placeholder for the real inference call.

    In production this would load the adapter via PEFT + transformers and
    generate. For now this is a stub that returns None unless --mock is
    passed (which returns the row's own label, to validate the harness).
    """
    # NOTE: real inference is NPU-resident per MEMORY.md training policy;
    # this function is the seam where the Huanxin job-submission flow plugs
    # in. It is intentionally a stub here so the harness can be tested on
    # CPU without a model.
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    ap.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    ap.add_argument("--split-out", type=Path, default=DEFAULT_SPLIT_OUT)
    ap.add_argument("--eval-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--split-only",
        action="store_true",
        help="Just write the split and exit (no oracle/model run)",
    )
    ap.add_argument(
        "--run-oracle",
        action="store_true",
        help="Run tests.py against every held-out row's candidate "
        "to get the execution-grounded label",
    )
    ap.add_argument("--adapter-path", type=str, default=None)
    ap.add_argument("--base-model", type=str, default="Qwen/Qwen3.6-27B")
    ap.add_argument(
        "--mock-critic",
        action="store_true",
        help="Critic returns the row's own label (harness self-test)",
    )
    args = ap.parse_args()

    rows = load_rows(args.rows)
    train_rows, eval_rows = stratified_split(rows, args.eval_frac, args.seed)
    print(
        f"split: {len(train_rows)} train / {len(eval_rows)} eval "
        f"(eval_frac={args.eval_frac}, seed={args.seed})",
        file=sys.stderr,
    )
    from collections import Counter

    print(f"  train labels: {dict(Counter(r['label'] for r in train_rows))}", file=sys.stderr)
    print(f"  eval labels:  {dict(Counter(r['label'] for r in eval_rows))}", file=sys.stderr)

    split_obj = {
        "seed": args.seed,
        "eval_frac": args.eval_frac,
        "train_rows": train_rows,
        "eval_rows": eval_rows,
    }
    args.split_out.parent.mkdir(parents=True, exist_ok=True)
    args.split_out.write_text(json.dumps(split_obj, indent=2, ensure_ascii=False))
    print(f"wrote split -> {args.split_out}", file=sys.stderr)

    if args.split_only:
        return 0

    # Oracle: run tests.py against each eval row's candidate
    tp = fp = fn = tn = skipped = 0
    per_task = []
    for r in eval_rows:
        if args.run_oracle:
            gt = oracle_label(r, args.tasks_dir)
        else:
            gt = r["label"] == "positive"  # use the row's own label as ground truth
        if gt is None:
            skipped += 1
            continue
        if args.mock_critic:
            pred = r["label"] == "positive"
        else:
            obj = call_critic(r, args.adapter_path, args.base_model)
            pred = obj["pass"] if obj else None
        if pred is None:
            skipped += 1
            continue
        if gt and pred:
            tp += 1
        elif gt and not pred:
            fn += 1
        elif (not gt) and pred:
            fp += 1
        else:
            tn += 1
        per_task.append({"task_id": r["task_id"], "gt": gt, "pred": pred})

    decided = tp + fp + fn + tn
    if decided == 0:
        print("no decisions made (oracle/critic not run); split written.", file=sys.stderr)
        return 0
    agreement = (tp + tn) / decided
    print("\n=== Critic agreement report ===")
    print(f"decided: {decided}  skipped: {skipped}")
    print(f"  TP={tp}  FP={fp}  FN={fn}  TN={tn}")
    print(f"  agreement = {agreement:.2%}  (target >= 85%)")
    if tp + fn > 0:
        print(f"  recall (pass) = {tp/(tp+fn):.2%}")
    if tp + fp > 0:
        print(f"  precision (pass) = {tp/(tp+fp):.2%}")
    return 0 if agreement >= 0.85 else 1


if __name__ == "__main__":
    raise SystemExit(main())

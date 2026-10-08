#!/usr/bin/env python3
"""mine_failures.py — structured failure table from eval outputs. Data-miner lane tool.

Reads eval result files (jsonl/json), classifies failures, emits a table
directly consumable by a relaunch config:
  {"task_id": ..., "class": syntax|import|api|algorithm|truncation|parse, "count": n, "example": line}

Usage:
    python3 harness/scripts/mine_failures.py <results.jsonl> [--format json|md]
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

CLASS_PATTERNS = [
    ("syntax", r"SyntaxError|syntax error|IndentationError"),
    ("import", r"ImportError|ModuleNotFoundError|cannot import"),
    ("api", r"AttributeError|TypeError|invalid argument|unexpected keyword"),
    ("truncation", r"truncated|max_tokens|token limit|too long"),
    ("parse", r"JSONDecodeError|parse error|failed to parse"),
    ("timeout", r"Timeout|timed out"),
    ("algorithm", r"AssertionError|wrong answer|incorrect|mismatch"),
]


def classify_error(text: str) -> str:
    """Classify one error string. <8 lines."""
    for cls, pat in CLASS_PATTERNS:
        if re.search(pat, str(text), re.IGNORECASE):
            return cls
    return "other"


def mine(results_path: Path) -> list[dict]:
    """Build failure table. <15 lines."""
    rows = []
    for line in results_path.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("passed") or rec.get("pass"):
            continue  # only failures
        task = rec.get("task_id") or rec.get("task") or "?"
        err = (rec.get("error") or rec.get("reason") or rec.get("output") or "")[:200]
        rows.append({"task_id": str(task), "class": classify_error(err), "example": err[:120]})
    # Aggregate: task × class → count
    agg = Counter((r["task_id"], r["class"]) for r in rows)
    out = []
    for (task, cls), n in sorted(agg.items()):
        ex = next(r["example"] for r in rows if r["task_id"] == task and r["class"] == cls)
        out.append({"task_id": task, "class": cls, "count": n, "example": ex})
    return out


def render_md(rows: list[dict]) -> str:
    """<8 lines."""
    if not rows:
        return "NO FAILURES"
    lines = ["| task_id | class | count | example |", "| --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['task_id']} | {r['class']} | {r['count']} | {r['example'][:60]} |")
    return "\n".join(lines)


def main() -> None:
    """<10 lines."""
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--format", choices=["json", "md"], default="json")
    args = ap.parse_args()
    rows = mine(Path(args.results))
    if args.format == "md":
        print(render_md(rows))
    else:
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Analyze the last batch's failure distribution and emit a weakness report.

Reads the RL-distill buffer (train_chatml_with_logits.jsonl or the
buffer's samples.jsonl) and aggregates per-(framework, topic, difficulty)
pass rates from the `metadata.student_exec.verdict` field. Writes a JSON
report that the pipeline's WeaknessReport consumes to bias the next
batch's question generation toward the student's weak cells.

Usage:
    python3 scripts/analyze_batch_weakness.py \\
        --buffer-dir data/generated/rl_distill_27b_v1 \\
        --output   data/generated/rl_distill_27b_v1/weakness_report.json \\
        [--batch-id round-7] \\
        [--min-cell-n 1]
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


def _iter_samples(buffer_dir: Path):
    """Yield sample dicts from the buffer directory."""
    # The BufferWriter writes samples to samples.jsonl (append-only).
    candidates = [
        buffer_dir / "samples.jsonl",
        buffer_dir / "train_chatml_with_logits.jsonl",
    ]
    for path in candidates:
        if path.is_file():
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
            return


def analyze(buffer_dir: Path, *, min_cell_n: int = 1) -> dict[str, Any]:
    """Aggregate pass rates per (framework, topic, difficulty) cell."""
    cells: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: {"n": 0, "pass": 0})
    n_total = 0
    for sample in _iter_samples(buffer_dir):
        meta = sample.get("metadata", {}) if isinstance(sample, dict) else {}
        fw = str(meta.get("framework", "unknown"))
        tp = str(meta.get("topic", "unknown"))
        df = str(meta.get("difficulty", "unknown"))
        student_exec = meta.get("student_exec") or {}
        verdict = student_exec.get("verdict", "ERROR")
        n_total += 1
        key = (fw, tp, df)
        cells[key]["n"] += 1
        if verdict == "PASS":
            cells[key]["pass"] += 1

    cell_list = []
    for (fw, tp, df), counts in cells.items():
        if counts["n"] < min_cell_n:
            continue
        pass_rate = counts["pass"] / max(counts["n"], 1)
        cell_list.append(
            {
                "framework": fw,
                "topic": tp,
                "difficulty": df,
                "pass_rate": round(pass_rate, 4),
                "n": counts["n"],
            }
        )
    # Sort by weakness (lowest pass rate first).
    cell_list.sort(key=lambda c: (c["pass_rate"], -c["n"]))
    return {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "buffer_dir": str(buffer_dir),
        "n_samples": n_total,
        "n_cells": len(cell_list),
        "cells": cell_list,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--buffer-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-id", default="", help="Optional human-readable batch identifier")
    parser.add_argument(
        "--min-cell-n",
        type=int,
        default=1,
        help="Minimum samples per cell to include in the report",
    )
    args = parser.parse_args()

    report = analyze(args.buffer_dir, min_cell_n=args.min_cell_n)
    if args.batch_id:
        report["batch_id"] = args.batch_id

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "stage": "weakness_report_written",
                "output": str(args.output),
                "n_samples": report["n_samples"],
                "n_cells": report["n_cells"],
                "weakest_5": report["cells"][:5],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

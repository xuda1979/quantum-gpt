#!/usr/bin/env python3
"""Prepare the UNIFIED DPO dataset — one adapter that fixes ALL error categories.

This merges the 5 per-error-category DPO lines into a single dataset:

  N1  universal-failure   (ref vs failing roll-out, execution-grounded)
  N3  import-path         (ref vs import-mutation)
  N6  format              (canonical vs prose-only / no-main / no-guard)
  N7  density-matrix      (ref vs type-precedence mutation)
  N10 traceback-repair    (failing+tb vs ref)

Rationale (2026-07-13 reorg): an adapter that fixes only ImportError is
useless if it produces prose-only output. The error categories are
complementary failure modes, not competing approaches, so the DPO pairs
must be unioned into one training set. Each pair is tagged with
`source_line` so ablation (train on N-1 lines, eval on the held-out
line) is still possible.

Output schema (one JSON object per line):
    {
      "prompt": [...],            # ChatML messages
      "chosen": [...],            # ChatML messages
      "rejected": [...],          # ChatML messages
      "negative_type": "import_error" | "prose_only" | "no_main" |
                        "no_guard" | "type_error" | "wrong_output" |
                        "traceback_repair",
      "source_line": "N1" | "N3" | "N6" | "N7" | "N10",
      "pair_id": "<16-hex>",
      "task_id": "..."            # when applicable
    }

Usage:
    python3 scripts/prepare_unified_dpo.py \
        --output data/generated/rd_lines_2026_07_13/unified_dpo_pairs.jsonl \
        --check

    # Regenerate only a subset (ablation):
    python3 scripts/prepare_unified_dpo.py --lines N1,N3,N6 --output ...
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
DEFAULT_OUT = REPO / "data/generated/rd_lines_2026_07_13/unified_dpo_pairs.jsonl"

# Each line: (source_line, script, extra-args)
# All per-line scripts emit either `failure_category` or `negative_type`;
# the unified script normalizes to `negative_type` for downstream consistency.
LINES = {
    "N1": {
        "script": "prepare_universal_failure_dpo.py",
        "extra_args": ["--check"],
    },
    "N3": {
        "script": "prepare_import_path_dpo.py",
        "extra_args": [],
    },
    "N6": {
        "script": "prepare_format_dpo_pairs.py",
        "extra_args": [
            "--check",
            "--input",
            "data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl",
        ],
    },
    "N7": {
        "script": "prepare_density_matrix_precedence_dpo.py",
        "extra_args": [],
    },
    "N10": {
        "script": "prepare_traceback_repair_dpo.py",
        "extra_args": [],
    },
}


def run_line(source_line: str, spec: dict, workdir: Path) -> Path:
    """Run one per-line prep script; return the path to its JSONL output."""
    out = workdir / f"{source_line.lower()}_dpo_pairs.jsonl"
    cmd = [sys.executable, str(SCRIPTS / spec["script"]), "--output", str(out)] + spec["extra_args"]
    print(f"[{source_line}] {' '.join(cmd)}", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, timeout=600)
    if proc.returncode != 0:
        print(f"[{source_line}] FAILED rc={proc.returncode}", file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit(1)
    # Stream the tail of stderr for visibility
    for line in proc.stderr.strip().splitlines()[-4:]:
        print(f"[{source_line}]   {line}", file=sys.stderr)
    return out


def tag_and_collect(path: Path, source_line: str) -> list[dict]:
    """Read a per-line JSONL, tag each row with source_line, normalize neg type.

    Different per-line scripts use different field names for the failure
    category (`failure_category` vs `negative_type`); normalize to
    `negative_type` so the unified dataset has one field.
    """
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            r["source_line"] = source_line
            # Normalize the negative-type field name across lines
            nt = r.get("negative_type") or r.get("failure_category") or "unknown"
            r["negative_type"] = nt
            rows.append(r)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--workdir",
        type=Path,
        default=REPO / "data/generated/rd_lines_2026_07_13/_unified_dpo_work",
    )
    ap.add_argument(
        "--lines",
        type=str,
        default=",".join(LINES.keys()),
        help="comma-separated subset of: " + ",".join(LINES.keys()),
    )
    ap.add_argument(
        "--check", action="store_true", help="pass --check to underlying scripts that support it"
    )
    args = ap.parse_args()

    selected = [s.strip().upper() for s in args.lines.split(",") if s.strip()]
    unknown = [s for s in selected if s not in LINES]
    if unknown:
        print(f"unknown line(s): {unknown}; valid: {list(LINES.keys())}", file=sys.stderr)
        return 2

    args.workdir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    per_line_counts = {}
    for sl in selected:
        spec = LINES[sl]
        if not args.check and "--check" in spec["extra_args"]:
            spec = {**spec, "extra_args": [a for a in spec["extra_args"] if a != "--check"]}
        path = run_line(sl, spec, args.workdir)
        rows = tag_and_collect(path, sl)
        per_line_counts[sl] = len(rows)
        all_rows.extend(rows)

    # Write unified output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Report
    from collections import Counter

    neg_dist = Counter(r["negative_type"] for r in all_rows)
    print("\n=== Unified DPO ===", file=sys.stderr)
    print(f"lines: {selected}", file=sys.stderr)
    print(f"per-line: {per_line_counts}", file=sys.stderr)
    print(f"total pairs: {len(all_rows)}", file=sys.stderr)
    print(f"negative_type distribution: {dict(neg_dist)}", file=sys.stderr)
    print(f"wrote -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

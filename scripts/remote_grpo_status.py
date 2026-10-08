#!/usr/bin/env python3
"""Compact FV-GSPO run status for the ASI2 monitoring loop.

Runs ON the training box (repo is synced to /root/work/software/quantum-gpt).
Finds the latest `outputs/grpo-27b-selfeval-*/grpo_step_metrics.jsonl` and
prints a compact JSON status: record count, route histogram, frontier yield,
all-fail share, repair-queue size, and the last record's key FV-GSPO fields.

Usage (on box):
    python3 scripts/remote_grpo_status.py [--outputs-dir outputs] [--queue path]

Local override for testing: --outputs-dir /tmp/... --queue /tmp/.../repair_queue.jsonl
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.is_file():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outputs-dir", default="outputs")
    p.add_argument("--queue", default=None, help="repair_queue.jsonl path (for size).")
    args = p.parse_args(argv)

    metrics_path: Path | None = None
    runs = sorted(glob.glob(os.path.join(args.outputs_dir, "grpo-27b-selfeval-*")), reverse=True)
    for run in runs:
        candidate = Path(run) / "grpo_step_metrics.jsonl"
        if candidate.is_file():
            metrics_path = candidate
            break

    if metrics_path is None:
        print(json.dumps({"status": "no_run_yet", "outputs_dir": args.outputs_dir}))
        return 0

    records = load_jsonl(metrics_path)
    if not records:
        print(json.dumps({"status": "no_records_yet", "metrics": str(metrics_path)}))
        return 0

    routes = Counter(str(r.get("route", "")) for r in records)
    probed = sum(1 for r in records if r.get("route"))
    rl_routes = sum(1 for r in records if r.get("route") in ("frontier_rl", "partial_repair_rl"))
    all_fail = sum(1 for r in records if bool(r.get("all_fail")))
    repair_queued = sum(1 for r in records if bool(r.get("repair_queued")))
    breaker_trips = [
        t for r in records if isinstance(r.get("breaker_trips"), list) for t in r["breaker_trips"]
    ]
    queue_size = 0
    if args.queue and Path(args.queue).is_file():
        queue_size = len(load_jsonl(Path(args.queue)))

    last = records[-1]
    keys = [
        "step",
        "task",
        "route",
        "pass_rate",
        "loss",
        "ratio_mean",
        "clip_low_fraction",
        "clip_high_fraction",
        "entropy_mean",
        "frontier_fraction",
        "repair_queued",
        "kl_beta",
        "skipped",
        "reason",
    ]
    status = {
        "status": "running",
        "metrics": str(metrics_path),
        "records": len(records),
        "routes": dict(sorted(routes.items())),
        "frontier_yield": (rl_routes / probed) if probed else None,
        "all_fail_share": (all_fail / probed) if probed else None,
        "repair_queued_steps": repair_queued,
        "repair_queue_size": queue_size,
        "breaker_trips": breaker_trips,
        "last": {k: last.get(k) for k in keys},
    }
    print(json.dumps(status, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

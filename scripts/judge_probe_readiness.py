#!/usr/bin/env python3
"""Judge whether the FV-GSPO short probe earned a long run (design gate).

The design says: "Do not launch a long run before the router produces a
healthy frontier yield on a short probe." This script turns that gate into a
deterministic verdict from the probe's `grpo_step_metrics.jsonl`:

- at least MIN_PROBED_RECORDS probed groups (routes recorded);
- frontier yield (share of probed groups routed frontier_rl/partial_repair_rl)
  >= MIN_FRONTIER_YIELD;
- mean GSPO clip fraction <= MAX_CLIP_FRACTION (clipping is a guardrail);
- entropy not collapsed (mean entropy >= MIN_ENTROPY when recorded);
- all-fail share <= MAX_ALL_FAIL_SHARE unless the repair stage is converting;
- no circuit-breaker trips.

Usage:
    python3 scripts/judge_probe_readiness.py --metrics <run>/grpo_step_metrics.jsonl \
        [--repair-converted <run>/repair_stage/repair_converted.jsonl]

Prints {"verdict": "ready"|"wait", "checks": {...}, "reason": "..."}.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_PROBED_RECORDS = 12
MIN_FRONTIER_YIELD = 0.30
MAX_CLIP_FRACTION = 0.50
MIN_ENTROPY = 0.5
MAX_ALL_FAIL_SHARE = 0.40


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


def count_repair_conversions(path: Path | None) -> int:
    if path is None or not path.is_file():
        return 0
    total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            if bool(json.loads(line).get("converted", False)):
                total += 1
        except json.JSONDecodeError:
            continue
    return total


def judge_probe(
    metrics_path: Path,
    repair_converted_path: Path | None = None,
) -> dict:
    records = load_jsonl(metrics_path)
    probed = [r for r in records if r.get("route")]
    if len(probed) < MIN_PROBED_RECORDS:
        return {
            "verdict": "wait",
            "checks": {"probed_records": len(probed), "required": MIN_PROBED_RECORDS},
            "reason": f"probe too short: {len(probed)}/{MIN_PROBED_RECORDS} probed records",
        }

    rl_routes = sum(1 for r in probed if r.get("route") in ("frontier_rl", "partial_repair_rl"))
    frontier_yield = rl_routes / len(probed)

    clip_values = [
        float(r["clip_low_fraction"]) + float(r["clip_high_fraction"])
        for r in probed
        if r.get("clip_low_fraction") is not None
    ]
    clip_mean = sum(clip_values) / len(clip_values) if clip_values else 0.0

    entropy_values = [float(r["entropy_mean"]) for r in probed if r.get("entropy_mean") is not None]
    entropy_mean = sum(entropy_values) / len(entropy_values) if entropy_values else None

    all_fail = sum(1 for r in probed if bool(r.get("all_fail")))
    all_fail_share = all_fail / len(probed)
    conversions = count_repair_conversions(repair_converted_path)

    breaker_trips = [
        t for r in records if isinstance(r.get("breaker_trips"), list) for t in r["breaker_trips"]
    ]

    checks = {
        "probed_records": len(probed),
        "frontier_yield": round(frontier_yield, 3),
        "clip_mean": round(clip_mean, 3),
        "entropy_mean": round(entropy_mean, 3) if entropy_mean is not None else None,
        "all_fail_share": round(all_fail_share, 3),
        "repair_conversions": conversions,
        "breaker_trips": len(breaker_trips),
    }
    failures: list[str] = []
    if frontier_yield < MIN_FRONTIER_YIELD:
        failures.append(
            f"frontier yield {frontier_yield:.2f} < {MIN_FRONTIER_YIELD} (router not finding "
            "learnable groups)"
        )
    if clip_mean > MAX_CLIP_FRACTION:
        failures.append(
            f"clip fraction {clip_mean:.2f} > {MAX_CLIP_FRACTION} (clipping is a guardrail)"
        )
    if entropy_mean is not None and entropy_mean < MIN_ENTROPY:
        failures.append(f"entropy collapsed {entropy_mean:.2f} < {MIN_ENTROPY}")
    if all_fail_share > MAX_ALL_FAIL_SHARE and conversions == 0:
        failures.append(
            f"all-fail share {all_fail_share:.2f} > {MAX_ALL_FAIL_SHARE} without repair conversion"
        )
    if breaker_trips:
        failures.append(f"{len(breaker_trips)} circuit-breaker trip(s)")

    if failures:
        return {
            "verdict": "wait",
            "checks": checks,
            "reason": "; ".join(failures),
        }
    return {
        "verdict": "ready",
        "checks": checks,
        "reason": "router frontier yield healthy; clips, entropy, all-fail share, breakers green",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--metrics", required=True, type=Path)
    p.add_argument("--repair-converted", default=None, type=Path)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.metrics.is_file():
        print(json.dumps({"verdict": "wait", "reason": f"no metrics at {args.metrics}"}))
        return 0
    result = judge_probe(args.metrics, args.repair_converted)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

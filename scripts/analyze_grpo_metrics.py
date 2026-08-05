#!/usr/bin/env python3
"""Analyze GRPO step metrics and emit a per-step CSV + summary.

Reads a `grpo_step_metrics.jsonl` file (written by `training/grpo_trainer.py`)
and emits:

1. A per-step CSV (`<out_prefix>.csv`) with columns including
   `step`, `task`, `mean_reward`, `pass_rate`, `dr_psi`,
   `dr_psi_init`, `dr_psi_warmup_steps`, `dr_psi_current_step`,
   and `dr_variance_correction_value`.
2. A summary JSON (`<out_prefix>.summary.json`) with aggregate
   statistics for the DR variance correction: min/max/mean/std of
   `dr_variance_correction_value`, whether it stayed finite and
   bounded, and the psi schedule that was applied.

The `dr_variance_correction` column is the key diagnostic for the
doubly_robust_quantum_grpo research method — it lets us plot the
correction magnitude over training steps and confirm it stays
finite and bounded (per the 2026-07-09 review item [MED]).

Usage:
    python3 scripts/analyze_grpo_metrics.py \
        --metrics <run_dir>/grpo_step_metrics.jsonl \
        --out-prefix <run_dir>/grpo_metrics_analysis
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file, skipping blank/malformed lines."""
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines rather than failing the whole analysis.
                continue
    return records


def _float_or_nan(value: Any) -> float:
    """Coerce to float, returning NaN for None/non-numeric."""
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _is_finite(value: float) -> bool:
    """True if value is a real number (not NaN, not inf)."""
    return not (math.isnan(value) or math.isinf(value))


def _finite_values(values: Iterable[float]) -> list[float]:
    """Filter to just the finite values."""
    return [v for v in values if _is_finite(v)]


def _summarize_dr(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate statistics for the DR variance correction term."""
    dr_values = [_float_or_nan(r.get("dr_variance_correction_value")) for r in records]
    finite_dr = _finite_values(dr_values)
    psi_values = [_float_or_nan(r.get("dr_psi")) for r in records]
    finite_psi = _finite_values(psi_values)

    summary: dict[str, Any] = {
        "total_steps": len(records),
        "dr_variance_correction": {
            "steps_with_value": len(finite_dr),
            "finite": len(finite_dr) == len(dr_values) if dr_values else True,
            "bounded": (all(abs(v) < 1e6 for v in finite_dr) if finite_dr else True),
        },
        "dr_psi": {
            "steps_with_value": len(finite_psi),
            "min": min(finite_psi) if finite_psi else None,
            "max": max(finite_psi) if finite_psi else None,
            "mean": statistics.fmean(finite_psi) if finite_psi else None,
            "stdev": statistics.pstdev(finite_psi) if len(finite_psi) > 1 else 0.0,
        },
    }
    if finite_dr:
        summary["dr_variance_correction"].update(
            {
                "min": min(finite_dr),
                "max": max(finite_dr),
                "mean": statistics.fmean(finite_dr),
                "stdev": statistics.pstdev(finite_dr) if len(finite_dr) > 1 else 0.0,
                "abs_mean": statistics.fmean(abs(v) for v in finite_dr),
                "abs_max": max(abs(v) for v in finite_dr),
            }
        )
    # Record the configured schedule if any step reported it.
    psi_init_values = [_float_or_nan(r.get("dr_psi_init")) for r in records]
    warmup_values = [
        r.get("dr_psi_warmup_steps") for r in records if r.get("dr_psi_warmup_steps") is not None
    ]
    finite_psi_init = _finite_values(psi_init_values)
    if finite_psi_init:
        summary["dr_psi"]["psi_init"] = finite_psi_init[0]
    if warmup_values:
        # Report the first non-zero warmup config we see (assume one schedule per run).
        first_nonzero = next((int(w) for w in warmup_values if int(w) > 0), 0)
        summary["dr_psi"]["warmup_steps"] = first_nonzero
    return summary


def _write_csv(records: list[dict[str, Any]], csv_path: Path) -> None:
    """Write a per-step CSV with the DR and FV-GSPO columns included."""
    # Stable column order; missing keys become empty strings.
    columns = [
        "step",
        "task",
        "domain",
        "mean_reward",
        "pass_rate",
        "syntax_rate",
        "interface_rate",
        "loss",
        "route",
        "all_fail",
        "repair_queued",
        "frontier_fraction",
        "entropy_mean",
        "ratio_mean",
        "clip_low_fraction",
        "clip_high_fraction",
        "seq_kl",
        "generation_tokens",
        "dr_psi",
        "dr_psi_init",
        "dr_psi_warmup_steps",
        "dr_psi_current_step",
        "dr_variance_correction_value",
        "dr_pair_mined",
        "dr_pair_reward_gap",
        "skipped",
        "reason",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = {col: record.get(col, "") for col in columns}
            # Normalize nested step values for CSV readability.
            for key in columns:
                if row[key] is None:
                    row[key] = ""
            writer.writerow(row)


def _summarize_fv_gspo(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate FV-GSPO diagnostics: routing, frontier yield, clipping, entropy.

    Mirrors the design's monitoring list (docs/frontier-verifier-gspo-design-2026-08-04.md
    §Monitoring): route fractions, frontier yield, all-fail share, clip
    fractions, sequence ratio, entropy, repair queue, and breaker trips.
    """
    routes: dict[str, int] = {}
    all_fail_steps = 0
    probed_steps = 0
    rl_route_steps = 0
    repair_queued_steps = 0
    clip_low_values: list[float] = []
    clip_high_values: list[float] = []
    ratio_values: list[float] = []
    seq_kl_values: list[float] = []
    entropy_values: list[float] = []
    frontier_fractions: list[float] = []
    breaker_trips: list[dict[str, Any]] = []
    generation_tokens = 0

    for record in records:
        route = record.get("route")
        if route is not None:
            routes[str(route)] = routes.get(str(route), 0) + 1
            probed_steps += 1
            if str(route) in ("frontier_rl", "partial_repair_rl"):
                rl_route_steps += 1
        if bool(record.get("all_fail")):
            all_fail_steps += 1
        if bool(record.get("repair_queued")):
            repair_queued_steps += 1
        for key, bucket in (
            ("clip_low_fraction", clip_low_values),
            ("clip_high_fraction", clip_high_values),
            ("ratio_mean", ratio_values),
            ("seq_kl", seq_kl_values),
            ("entropy_mean", entropy_values),
            ("frontier_fraction", frontier_fractions),
        ):
            value = record.get(key)
            if value is not None and _is_finite(_float_or_nan(value)):
                bucket.append(float(value))
        trips = record.get("breaker_trips")
        if isinstance(trips, list):
            breaker_trips.extend(trips)
        try:
            generation_tokens += int(record.get("generation_tokens") or 0)
        except (TypeError, ValueError):
            pass

    def _mean(values: list[float]) -> float | None:
        return statistics.fmean(values) if values else None

    summary: dict[str, Any] = {
        "probed_steps": probed_steps,
        "route_counts": dict(sorted(routes.items())),
        "frontier_yield": (rl_route_steps / probed_steps) if probed_steps else None,
        "all_fail_share": (all_fail_steps / probed_steps) if probed_steps else None,
        "repair_queued_steps": repair_queued_steps,
        "clip_low_fraction_mean": _mean(clip_low_values),
        "clip_high_fraction_mean": _mean(clip_high_values),
        "ratio_mean": _mean(ratio_values),
        "seq_kl_mean": _mean(seq_kl_values),
        "entropy_mean": _mean(entropy_values),
        "frontier_fraction_last": frontier_fractions[-1] if frontier_fractions else None,
        "generation_tokens_total": generation_tokens,
        "breaker_trips": breaker_trips,
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze GRPO step metrics, emitting a CSV + DR summary."
    )
    parser.add_argument(
        "--metrics",
        required=True,
        type=Path,
        help="Path to grpo_step_metrics.jsonl",
    )
    parser.add_argument(
        "--out-prefix",
        required=True,
        type=Path,
        help="Output prefix; writes <prefix>.csv and <prefix>.summary.json",
    )
    args = parser.parse_args(argv)

    metrics_path: Path = args.metrics
    out_prefix: Path = args.out_prefix
    if not metrics_path.is_file():
        print(f"error: metrics file not found: {metrics_path}", file=sys.stderr)
        return 2

    records = _load_jsonl(metrics_path)
    if not records:
        print(f"error: no records in {metrics_path}", file=sys.stderr)
        return 3

    csv_path = out_prefix.with_suffix(".csv")
    summary_path = out_prefix.with_suffix(".summary.json")

    _write_csv(records, csv_path)
    summary = {
        "metrics_file": str(metrics_path),
        "total_steps": len(records),
        "dr_summary": _summarize_dr(records),
        "fv_gspo_summary": _summarize_fv_gspo(records),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"wrote {csv_path}")
    print(f"wrote {summary_path}")
    # Print a one-line DR health verdict for quick CLI scanning.
    dr = summary["dr_summary"]["dr_variance_correction"]
    verdict = "OK"
    if not dr.get("finite", True):
        verdict = "NON-FINITE VALUES PRESENT"
    elif not dr.get("bounded", True):
        verdict = "UNBOUNDED VALUES PRESENT"
    print(f"dr_variance_correction: {verdict} (steps={dr.get('steps_with_value', 0)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

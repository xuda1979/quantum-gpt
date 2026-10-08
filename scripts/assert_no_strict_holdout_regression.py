#!/usr/bin/env python3
"""Fail when a same-model strict-holdout comparison regresses versus base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--min-strict-delta-passes", type=int, default=0)
    parser.add_argument("--min-full-delta-passes", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_int(mapping: dict[str, Any], key: str, *, default: int | None = None) -> int:
    value = mapping.get(key, default)
    if not isinstance(value, int):
        raise SystemExit(f"Expected integer field {key!r}, got {value!r}")
    return value


def extract_metrics(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    strict_block = payload.get("strict_override")
    if not isinstance(strict_block, dict):
        raise SystemExit(f"{path} is missing strict_override")

    # Current comparison schema from scripts/build_strict_scorecard_comparison.py
    if payload.get("kind") == "strict_override_comparison":
        full_block = payload.get("full_scorecard")
        if not isinstance(full_block, dict):
            raise SystemExit(f"{path} is missing full_scorecard")
        return {
            "schema": "strict_override_comparison",
            "base_passes": _as_int(strict_block, "base_passes"),
            "base_total": _as_int(strict_block, "base_total"),
            "candidate_passes": _as_int(strict_block, "adapter_passes"),
            "candidate_total": _as_int(strict_block, "adapter_total"),
            "strict_delta_passes": _as_int(strict_block, "adapter_minus_base_passes"),
            "full_delta_passes": _as_int(full_block, "candidate_minus_base_passes"),
            "baseline_label": str((payload.get("baseline") or {}).get("label") or ""),
            "candidate_label": str((payload.get("candidate") or {}).get("label") or ""),
        }

    # Legacy OmniCoder comparison schema.
    if {"base_passes", "adapter_passes", "adapter_minus_base_passes"} <= set(strict_block):
        return {
            "schema": "legacy_strict_override",
            "base_passes": _as_int(strict_block, "base_passes"),
            "base_total": _as_int(strict_block, "base_total"),
            "candidate_passes": _as_int(strict_block, "adapter_passes"),
            "candidate_total": _as_int(strict_block, "adapter_total"),
            "strict_delta_passes": _as_int(strict_block, "adapter_minus_base_passes"),
            "full_delta_passes": None,
            "baseline_label": str(payload.get("base_label") or "base"),
            "candidate_label": str(payload.get("adapter_label") or "adapter"),
        }

    raise SystemExit(f"Unsupported comparison schema in {path}")


def main() -> int:
    args = parse_args()
    payload = load_json(args.comparison)
    metrics = extract_metrics(payload, args.comparison)

    failures: list[str] = []
    strict_delta = int(metrics["strict_delta_passes"])
    if strict_delta < args.min_strict_delta_passes:
        failures.append(f"strict delta {strict_delta} < required {args.min_strict_delta_passes}")

    full_delta = metrics["full_delta_passes"]
    if args.min_full_delta_passes is not None:
        if full_delta is None:
            failures.append("full-scorecard delta unavailable for requested full-delta gate")
        elif int(full_delta) < args.min_full_delta_passes:
            failures.append(f"full delta {int(full_delta)} < required {args.min_full_delta_passes}")

    result = {
        "kind": "strict_holdout_regression_gate",
        "comparison": str(args.comparison.resolve()),
        "schema": metrics["schema"],
        "baseline_label": metrics["baseline_label"],
        "candidate_label": metrics["candidate_label"],
        "base_strict_score": f"{metrics['base_passes']}/{metrics['base_total']}",
        "candidate_strict_score": f"{metrics['candidate_passes']}/{metrics['candidate_total']}",
        "strict_delta_passes": strict_delta,
        "full_delta_passes": full_delta,
        "min_strict_delta_passes": args.min_strict_delta_passes,
        "min_full_delta_passes": args.min_full_delta_passes,
        "ok": not failures,
        "failures": failures,
    }

    rendered = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

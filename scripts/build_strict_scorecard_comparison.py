#!/usr/bin/env python3
"""Build a same-protocol comparison summary from scorecard JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-scorecard", type=Path, required=True)
    parser.add_argument("--baseline-label", required=True)
    parser.add_argument("--candidate-scorecard", type=Path, required=True)
    parser.add_argument("--candidate-label", required=True)
    parser.add_argument("--reference-scorecard", type=Path, default=None)
    parser.add_argument("--reference-label", default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _count_passes(results: list[dict[str, Any]]) -> int:
    return sum(1 for item in results if item.get("passed"))


def summarize_scorecard(label: str, scorecard_path: Path) -> dict[str, Any]:
    payload = load_json(scorecard_path)
    results = payload.get("results") or []
    overrides = [item for item in results if item.get("source") == "override"]
    references = [item for item in results if item.get("source") == "reference"]
    failed_overrides = [item for item in overrides if not item.get("passed")]
    return {
        "label": label,
        "scorecard": str(scorecard_path.resolve()),
        "overall_passes": _count_passes(results),
        "overall_total": len(results),
        "reference_passes": _count_passes(references),
        "reference_total": len(references),
        "override_passes": _count_passes(overrides),
        "override_total": len(overrides),
        "override_pass_rate": (_count_passes(overrides) / len(overrides)) if overrides else None,
        "failed_override_task_ids": [
            str(item.get("id")) for item in failed_overrides if item.get("id")
        ],
    }


def build_delta_block(
    base: dict[str, Any], candidate: dict[str, Any], *, passes_key: str, total_key: str
) -> dict[str, Any]:
    base_passes = int(base[passes_key])
    candidate_passes = int(candidate[passes_key])
    base_total = int(base[total_key])
    candidate_total = int(candidate[total_key])
    if base_total != candidate_total:
        raise SystemExit(
            f"Mismatched totals for comparison: {base['label']} has {base_total}, "
            f"but {candidate['label']} has {candidate_total} for {total_key}."
        )
    total = base_total
    return {
        "base_passes": base_passes,
        "base_total": total,
        "candidate_passes": candidate_passes,
        "candidate_total": total,
        "candidate_minus_base_passes": candidate_passes - base_passes,
        "candidate_minus_base_pass_rate": ((candidate_passes - base_passes) / total)
        if total
        else None,
    }


def main() -> int:
    args = parse_args()
    baseline = summarize_scorecard(args.baseline_label, args.baseline_scorecard)
    candidate = summarize_scorecard(args.candidate_label, args.candidate_scorecard)
    result: dict[str, Any] = {
        "kind": "strict_override_comparison",
        "baseline": baseline,
        "candidate": candidate,
        "strict_override": {
            "base_passes": baseline["override_passes"],
            "base_total": baseline["override_total"],
            "adapter_passes": candidate["override_passes"],
            "adapter_total": candidate["override_total"],
            "adapter_minus_base_passes": candidate["override_passes"] - baseline["override_passes"],
            "adapter_minus_base_pass_rate": (
                (candidate["override_passes"] - baseline["override_passes"])
                / baseline["override_total"]
                if baseline["override_total"]
                else None
            ),
        },
        "full_scorecard": build_delta_block(
            baseline,
            candidate,
            passes_key="overall_passes",
            total_key="overall_total",
        ),
    }

    if args.reference_scorecard is not None:
        reference_label = args.reference_label or "reference"
        reference = summarize_scorecard(reference_label, args.reference_scorecard)
        result["reference"] = reference
        result["baseline_vs_reference"] = {
            "override": build_delta_block(
                reference,
                baseline,
                passes_key="override_passes",
                total_key="override_total",
            ),
            "full_scorecard": build_delta_block(
                reference,
                baseline,
                passes_key="overall_passes",
                total_key="overall_total",
            ),
        }
        result["candidate_vs_reference"] = {
            "override": build_delta_block(
                reference,
                candidate,
                passes_key="override_passes",
                total_key="override_total",
            ),
            "full_scorecard": build_delta_block(
                reference,
                candidate,
                passes_key="overall_passes",
                total_key="overall_total",
            ),
        }

    rendered = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Aggregate Qwen strict-holdout comparison artifacts into one table-ready JSON."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_INPUT_GLOB = "reports/qwen25_strict_holdout_base_vs_*.json"
DEFAULT_OUTPUT = Path("reports/qwen25_strict_holdout_comparison_table.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-glob",
        action="append",
        default=[],
        help=(
            "Glob pattern for strict-holdout comparison JSON artifacts. "
            f"Defaults to {DEFAULT_INPUT_GLOB!r} when omitted."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Where to write the aggregated JSON artifact (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_text(passes: int, total: int) -> str:
    return f"{passes}/{total}"


def rate_to_percent(rate: float | None) -> float | None:
    if rate is None:
        return None
    return rate * 100.0


def _as_int(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Expected integer field {key!r}, got {value!r}")
    return value


def build_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("kind") != "strict_override_comparison":
        raise ValueError(f"{path} is not a strict_override_comparison artifact")

    baseline = payload.get("baseline")
    candidate = payload.get("candidate")
    strict_override = payload.get("strict_override")
    full_scorecard = payload.get("full_scorecard")

    if not isinstance(baseline, dict) or not isinstance(candidate, dict):
        raise ValueError(f"{path} is missing baseline/candidate blocks")
    if not isinstance(strict_override, dict) or not isinstance(full_scorecard, dict):
        raise ValueError(f"{path} is missing strict/full comparison blocks")

    base_strict_passes = _as_int(strict_override, "base_passes")
    base_strict_total = _as_int(strict_override, "base_total")
    finetuned_strict_passes = _as_int(strict_override, "adapter_passes")
    finetuned_strict_total = _as_int(strict_override, "adapter_total")
    strict_delta_passes = _as_int(strict_override, "adapter_minus_base_passes")

    base_full_passes = _as_int(full_scorecard, "base_passes")
    base_full_total = _as_int(full_scorecard, "base_total")
    finetuned_full_passes = _as_int(full_scorecard, "candidate_passes")
    finetuned_full_total = _as_int(full_scorecard, "candidate_total")
    full_delta_passes = _as_int(full_scorecard, "candidate_minus_base_passes")

    return {
        "comparison_id": path.stem,
        "comparison_path": str(path.resolve()),
        "baseline_label": str(baseline.get("label") or ""),
        "baseline_scorecard": str(baseline.get("scorecard") or ""),
        "finetuned_label": str(candidate.get("label") or ""),
        "finetuned_scorecard": str(candidate.get("scorecard") or ""),
        "base_strict_passes": base_strict_passes,
        "base_strict_total": base_strict_total,
        "base_strict_score": score_text(base_strict_passes, base_strict_total),
        "finetuned_strict_passes": finetuned_strict_passes,
        "finetuned_strict_total": finetuned_strict_total,
        "finetuned_strict_score": score_text(finetuned_strict_passes, finetuned_strict_total),
        "strict_delta_passes": strict_delta_passes,
        "strict_delta_percentage_points": rate_to_percent(
            strict_override.get("adapter_minus_base_pass_rate")
        ),
        "base_full_passes": base_full_passes,
        "base_full_total": base_full_total,
        "base_full_score": score_text(base_full_passes, base_full_total),
        "finetuned_full_passes": finetuned_full_passes,
        "finetuned_full_total": finetuned_full_total,
        "finetuned_full_score": score_text(finetuned_full_passes, finetuned_full_total),
        "full_delta_passes": full_delta_passes,
        "full_delta_percentage_points": rate_to_percent(
            full_scorecard.get("candidate_minus_base_pass_rate")
        ),
        "baseline_failed_override_task_ids": list(baseline.get("failed_override_task_ids") or []),
        "finetuned_failed_override_task_ids": list(candidate.get("failed_override_task_ids") or []),
    }


def collect_comparison_paths(input_globs: list[str]) -> list[Path]:
    globs = input_globs or [DEFAULT_INPUT_GLOB]
    seen: set[Path] = set()
    paths: list[Path] = []
    for pattern in globs:
        for path in sorted(Path().glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            paths.append(path)
    return paths


def sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -int(row["strict_delta_passes"]),
            -float(row["strict_delta_percentage_points"] or 0.0),
            -int(row["full_delta_passes"]),
            -float(row["full_delta_percentage_points"] or 0.0),
            str(row["finetuned_label"]),
            str(row["comparison_id"]),
        ),
    )


def build_table_artifact(input_globs: list[str]) -> dict[str, Any]:
    comparison_paths = collect_comparison_paths(input_globs)
    if not comparison_paths:
        raise SystemExit(f"No comparison artifacts matched: {input_globs or [DEFAULT_INPUT_GLOB]}")

    rows = [build_row(path, load_json(path)) for path in comparison_paths]
    rows = sort_rows(rows)

    baseline_labels = sorted({row["baseline_label"] for row in rows})
    baseline_scorecards = sorted({row["baseline_scorecard"] for row in rows})
    return {
        "kind": "strict_holdout_comparison_table",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_globs": input_globs or [DEFAULT_INPUT_GLOB],
        "comparison_count": len(rows),
        "baseline_consistent": len(baseline_labels) == 1 and len(baseline_scorecards) == 1,
        "baseline_labels": baseline_labels,
        "baseline_scorecards": baseline_scorecards,
        "table_columns": [
            "comparison_id",
            "finetuned_label",
            "base_strict_score",
            "finetuned_strict_score",
            "strict_delta_passes",
            "strict_delta_percentage_points",
            "base_full_score",
            "finetuned_full_score",
            "full_delta_passes",
            "full_delta_percentage_points",
        ],
        "rows": rows,
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(rendered)
        tmp_path = Path(handle.name)
    tmp_path.replace(path)


def main() -> int:
    args = parse_args()
    artifact = build_table_artifact(args.input_glob)
    write_json_atomic(args.output, artifact)
    print(
        json.dumps(
            {"output": str(args.output), "comparison_count": artifact["comparison_count"]}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

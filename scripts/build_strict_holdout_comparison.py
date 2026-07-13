#!/usr/bin/env python3
"""Build a same-protocol strict-holdout comparison from two override summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-summary", type=Path, required=True)
    parser.add_argument("--adapter-summary", type=Path, required=True)
    parser.add_argument("--base-label", default="base")
    parser.add_argument("--adapter-label", default="adapter")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_int(payload: dict[str, Any], key: str, path: Path) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise SystemExit(f"{path} missing integer field: {key}")
    return value


def _rate(passes: int, total: int) -> float | None:
    if total <= 0:
        return None
    return passes / total


def main() -> int:
    args = parse_args()
    base_summary = load_json(args.base_summary)
    adapter_summary = load_json(args.adapter_summary)

    base_passes = _require_int(base_summary, "override_passes", args.base_summary)
    base_total = _require_int(base_summary, "override_total", args.base_summary)
    adapter_passes = _require_int(adapter_summary, "override_passes", args.adapter_summary)
    adapter_total = _require_int(adapter_summary, "override_total", args.adapter_summary)

    base_full_passes = _require_int(base_summary, "full_passes", args.base_summary)
    base_full_total = _require_int(base_summary, "full_total", args.base_summary)
    adapter_full_passes = _require_int(adapter_summary, "full_passes", args.adapter_summary)
    adapter_full_total = _require_int(adapter_summary, "full_total", args.adapter_summary)

    output = {
        "kind": "strict_override_comparison",
        "base_label": args.base_label,
        "adapter_label": args.adapter_label,
        "base_summary": str(args.base_summary.resolve()),
        "adapter_summary": str(args.adapter_summary.resolve()),
        "strict_override": {
            "base_passes": base_passes,
            "base_total": base_total,
            "base_pass_rate": _rate(base_passes, base_total),
            "adapter_passes": adapter_passes,
            "adapter_total": adapter_total,
            "adapter_pass_rate": _rate(adapter_passes, adapter_total),
            "adapter_minus_base_passes": adapter_passes - base_passes,
            "adapter_minus_base_pass_rate": _rate(adapter_passes, adapter_total)
            - _rate(base_passes, base_total),
        },
        "full_scorecard": {
            "base_passes": base_full_passes,
            "base_total": base_full_total,
            "base_pass_rate": _rate(base_full_passes, base_full_total),
            "adapter_passes": adapter_full_passes,
            "adapter_total": adapter_full_total,
            "adapter_pass_rate": _rate(adapter_full_passes, adapter_full_total),
            "adapter_minus_base_passes": adapter_full_passes - base_full_passes,
            "adapter_minus_base_pass_rate": _rate(adapter_full_passes, adapter_full_total)
            - _rate(base_full_passes, base_full_total),
        },
    }

    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

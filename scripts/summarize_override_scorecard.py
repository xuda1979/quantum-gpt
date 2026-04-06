#!/usr/bin/env python3
"""Summarize override-only results from a full scorecard.

This is useful for held-out eval runs where the runner fills non-overridden
tasks from reference candidates; the meaningful metric is the override subset.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorecard", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None, help="Optional path to write the JSON summary.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    scorecard = load_json(args.scorecard)
    results = scorecard.get("results", [])
    overrides = [result for result in results if result.get("source") == "override"]
    if not overrides:
        raise SystemExit(f"No override results found in {args.scorecard}")

    passed = sum(1 for result in overrides if result.get("passed"))
    failed = [result for result in overrides if not result.get("passed")]
    by_domain = Counter(str(result.get("domain", "unknown")) for result in overrides)
    by_category = Counter(str(result.get("category", "unknown")) for result in overrides)

    summary = {
        "scorecard": str(args.scorecard.resolve()),
        "override_total": len(overrides),
        "override_passes": passed,
        "override_failures": len(overrides) - passed,
        "override_pass_rate": passed / len(overrides),
        "domains": dict(sorted(by_domain.items())),
        "categories": dict(sorted(by_category.items())),
        "failed_task_ids": [result["id"] for result in failed],
        "failed_tasks": [
            {
                "id": result["id"],
                "name": result.get("name"),
                "domain": result.get("domain"),
                "category": result.get("category"),
                "error_type": result.get("error_type"),
                "first_detail": next(iter(result.get("details", [])), None),
                "candidate_path": result.get("candidate_path"),
            }
            for result in failed
        ],
    }

    if args.output is not None:
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

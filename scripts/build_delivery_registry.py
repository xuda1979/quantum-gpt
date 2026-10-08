#!/usr/bin/env python3
"""Build a single validated registry for model, handoff, and paper deliverables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.delivery_registry import ROOT, build_delivery_registry, write_delivery_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Workspace root to scan. Defaults to the current repo root.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts/delivery-registry/index.json",
        help="Output path for the generated registry JSON.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if the generated registry reports missing referenced artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_delivery_registry(args.root.resolve())
    out_path = write_delivery_registry(payload, args.out.resolve())
    print(
        json.dumps(
            {"out_path": str(out_path), "summary": payload["summary"], "ok": payload["ok"]},
            indent=2,
        )
    )
    if args.check and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

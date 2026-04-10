#!/usr/bin/env python3
"""Resolve a local Python interpreter that meets a minimum version."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_python import parse_min_version, resolve_python_interpreter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-version", default="3.10", help="Minimum required Python version, e.g. 3.10")
    parser.add_argument(
        "--print-path",
        action="store_true",
        help="Print only the resolved interpreter path and exit non-zero if none is available",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = resolve_python_interpreter(min_version=parse_min_version(args.min_version))
    if args.print_path:
        selected_path = result.get("selected_path")
        if not selected_path:
            return 1
        print(selected_path)
        return 0

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

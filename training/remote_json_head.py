#!/usr/bin/env python3
"""Print a bounded prefix of a JSON/text artifact for reliable Huanxin shell readback."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Remote file to read")
    parser.add_argument(
        "--chars",
        type=int,
        default=3000,
        help="Maximum number of characters to print",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text = args.path.read_text(encoding="utf-8")
    print(text[: args.chars])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

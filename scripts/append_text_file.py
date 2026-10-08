#!/usr/bin/env python3
import argparse
import pathlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append literal text to a file")
    parser.add_argument("--path", required=True)
    parser.add_argument("--text", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = pathlib.Path(args.path)
    with path.open("a", encoding="ascii") as handle:
        handle.write(args.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

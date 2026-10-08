#!/usr/bin/env python3
import argparse
import base64
import pathlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode a base64 text file")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    encoded = pathlib.Path(args.input).read_text(encoding="ascii")
    pathlib.Path(args.output).write_bytes(base64.b64decode(encoded))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

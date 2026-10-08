#!/usr/bin/env python3
import argparse
import pathlib
import sys
import zipfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a wheelhouse directory")
    parser.add_argument("--wheel-root", required=True, help="Directory containing .whl files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wheel_root = pathlib.Path(args.wheel_root)
    paths = sorted(wheel_root.glob("*.whl"))
    print("wheel_count=" + str(len(paths)))
    if not paths:
        print("no wheels found", file=sys.stderr)
        return 2

    for path in paths:
        ok = zipfile.is_zipfile(path)
        print(str(path) + " zip=" + str(ok))
        if not ok:
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

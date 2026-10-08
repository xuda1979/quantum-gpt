#!/usr/bin/env python3
"""Send a command to the local ai2 Huanxin daemon file IPC."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

IPC_DIR = Path("/tmp/huanxin-daemon-ai2.ipc")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--wait-ms", type=int, default=30000)
    parser.add_argument("--timeout-ms", type=int, default=45000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not IPC_DIR.exists():
        raise SystemExit(f"IPC dir missing: {IPC_DIR}")

    request_id = f"{int(time.time() * 1000)}-{Path(sys.argv[0]).stem}"
    request_path = IPC_DIR / f"{request_id}.request.json"
    response_path = IPC_DIR / f"{request_id}.response.json"
    request_path.write_text(
        json.dumps({"command": args.command, "waitMs": args.wait_ms}, ensure_ascii=False),
        encoding="utf-8",
    )

    deadline = time.time() + (args.timeout_ms / 1000.0)
    while time.time() < deadline:
        if response_path.exists():
            sys.stdout.write(response_path.read_text(encoding="utf-8"))
            try:
                request_path.unlink()
            except FileNotFoundError:
                pass
            try:
                response_path.unlink()
            except FileNotFoundError:
                pass
            return 0
        time.sleep(0.2)

    raise SystemExit(f"Timed out waiting for {response_path}")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fetch a remote ASI2 text file through the huanxin daemon, wrap-proof.

C-10446: the old marker+sed chunking broke two ways — (1) the terminal wraps
long lines into extra rows so line counts mismatched, and (2) large chunks
scrolled the begin/end markers off the captured viewport. The proven fix
(c10175_harvest pattern): gzip | base64 -w0 on the box, dd-chunk the single
base64 token, strip ALL whitespace when rejoining, gunzip locally.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PART_BYTES = 3000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-path", required=True)
    parser.add_argument("--local-path", required=True, type=Path)
    parser.add_argument("--part-bytes", type=int, default=PART_BYTES)
    parser.add_argument("--wait-ms", type=int, default=30000)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--validate-json", action="store_true")
    return parser.parse_args()


def run_ai2(command: str, wait_ms: int) -> dict:
    result = subprocess.run(
        [
            "node",
            str(ROOT / "browser-automation/huanxin_shell_exec.js"),
            "ASI2",
            "--require-daemon",
            "--wait-ms",
            str(wait_ms),
            "--command",
            command,
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def run_ai2_output(command: str, wait_ms: int, retries: int) -> str:
    """Run a command and return whitespace-stripped terminal output.

    base64 -w0 emits one long token; terminal wrapping only inserts
    newlines/spaces INSIDE that token, so stripping all whitespace is exact.
    """
    last_error: Exception | None = None
    for _ in range(max(1, retries)):
        try:
            payload = run_ai2(command, wait_ms)
            if payload.get("ok") is False or payload.get("commandOk") is False:
                raise RuntimeError(f"box command failed: {payload.get('output', '')[:200]}")
            return "".join(str(payload.get("output", "")).split())
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"failed after {retries} attempts: {command[:120]}: {last_error}")


def main() -> int:
    args = parse_args()
    remote = args.remote_path

    b64_len = int(
        run_ai2_output(f"gzip -c {remote} | base64 -w0 | wc -c", args.wait_ms, args.retries)
    )
    n_parts = (b64_len + args.part_bytes - 1) // args.part_bytes
    print(f"[fetch] remote={remote} gz_b64_bytes={b64_len} parts={n_parts}", flush=True)

    chunks: list[str] = []
    for i in range(n_parts):
        skip = i * args.part_bytes
        body = run_ai2_output(
            f"gzip -c {remote} | base64 -w0 | dd bs=1 skip={skip} count={args.part_bytes} 2>/dev/null",
            args.wait_ms,
            args.retries,
        )
        if not body:
            raise RuntimeError(f"empty part {i} (skip={skip})")
        chunks.append(body)
        print(f"[fetch] part {i + 1}/{n_parts} chars={len(body)}", flush=True)

    data = gzip.decompress(base64.b64decode("".join(chunks)))
    text = data.decode("utf-8")
    if args.validate_json:
        # JSONL: validate per-line, not whole-file
        for line in text.splitlines():
            if line.strip():
                json.loads(line)
    args.local_path.parent.mkdir(parents=True, exist_ok=True)
    args.local_path.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "remote_path": remote,
                "local_path": str(args.local_path),
                "line_count": len(text.splitlines()),
                "bytes": len(data),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

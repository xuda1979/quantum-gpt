#!/usr/bin/env python3
"""Fetch a remote ai2 text file through huanxin_shell_exec.js in line chunks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-path", required=True)
    parser.add_argument("--local-path", type=Path, required=True)
    parser.add_argument("--chunk-lines", type=int, default=30)
    parser.add_argument("--wait-ms", type=int, default=30000)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--validate-json", action="store_true")
    return parser.parse_args()


def run_ai2(command: str, wait_ms: int) -> dict:
    result = subprocess.run(
        [
            "node",
            str(ROOT / "browser-automation/huanxin_shell_exec.js"),
            "ai2",
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


def extract_between(payload: dict, begin_marker: str, end_marker: str) -> str:
    combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
    match = re.search(
        re.escape(begin_marker) + r"\n(.*?)\n" + re.escape(end_marker), combined, re.S
    )
    if match is None:
        raise RuntimeError(f"markers not found: {begin_marker} .. {end_marker}")
    return match.group(1)


def fetch_chunk(
    remote_path: str, start_line: int, end_line: int, wait_ms: int, retries: int
) -> str:
    expected_lines = end_line - start_line + 1
    command = (
        "cd /root/work/quantum-gpt && "
        "printf '__HX_CHUNK_BEGIN__\\n'; "
        f"sed -n {start_line},{end_line}p {remote_path}; "
        "printf '\\n__HX_CHUNK_END__\\n'"
    )
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            payload = run_ai2(command, wait_ms)
            chunk = extract_between(payload, "__HX_CHUNK_BEGIN__", "__HX_CHUNK_END__")
            got_lines = len(chunk.splitlines())
            if got_lines != expected_lines:
                raise RuntimeError(
                    f"line_count_mismatch chunk={start_line}-{end_line} expected={expected_lines} got={got_lines}"
                )
            return chunk
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries:
                break
            time.sleep(1.0)
    raise RuntimeError(f"failed chunk {start_line}-{end_line}: {last_error}") from last_error


def main() -> int:
    args = parse_args()
    meta_payload = run_ai2(
        "cd /root/work/quantum-gpt && "
        "printf '__HX_META_BEGIN__\\n'; "
        f"wc -l {args.remote_path}; "
        "printf '\\n__HX_META_END__\\n'",
        args.wait_ms,
    )
    meta_text = extract_between(meta_payload, "__HX_META_BEGIN__", "__HX_META_END__").strip()
    line_count = int(meta_text.split()[0])

    chunks: list[str] = []
    for start_line in range(1, line_count + 1, args.chunk_lines):
        end_line = min(line_count, start_line + args.chunk_lines - 1)
        chunks.append(
            fetch_chunk(args.remote_path, start_line, end_line, args.wait_ms, args.retries)
        )

    text = "\n".join(chunks) + "\n"
    if args.validate_json:
        json.loads(text)
    args.local_path.parent.mkdir(parents=True, exist_ok=True)
    args.local_path.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "remote_path": args.remote_path,
                "local_path": str(args.local_path),
                "line_count": line_count,
                "chunk_lines": args.chunk_lines,
                "chunks": len(chunks),
                "bytes": args.local_path.stat().st_size,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Upload a small local file into the ai2 workspace through the daemon-backed shell."""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_path", type=Path)
    parser.add_argument("remote_path")
    parser.add_argument("--wait-ms", type=int, default=15000)
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument("--skip-daemon", action="store_true")
    return parser.parse_args()


def run_local(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), check=True, text=True, capture_output=True)


def ai2_exec(command: str, *, wait_ms: int, skip_daemon: bool) -> dict:
    cmd = [
        "node",
        str(ROOT / "browser-automation/huanxin_shell_exec.js"),
        "ai2",
    ]
    cmd.append("--skip-daemon" if skip_daemon else "--require-daemon")
    cmd.extend(
        [
            "--wait-ms",
            str(wait_ms),
            "--command",
            command,
        ]
    )
    result = run_local(cmd)
    return json.loads(result.stdout)


def extract_ai2_output(response: dict) -> str:
    after = response.get("after")
    if isinstance(after, str):
        matches = list(
            re.finditer(
                r"(?ms)^(__OC_[A-Za-z0-9_]+_START__)\n(.*?)\n^(__OC_[A-Za-z0-9_]+_END__)$",
                after,
            )
        )
        if matches:
            return matches[-1].group(2).strip()
    direct_output = response.get("output")
    if isinstance(direct_output, str):
        return direct_output.strip()
    return ""


def ai2_exec_output(command: str, *, wait_ms: int, skip_daemon: bool) -> str:
    response = ai2_exec(command, wait_ms=wait_ms, skip_daemon=skip_daemon)
    if not response.get("ok"):
        raise RuntimeError(json.dumps(response, ensure_ascii=False, indent=2))
    return extract_ai2_output(response)


def upload_file_b64_in_chunks(
    local_path: Path,
    remote_path: str,
    *,
    wait_ms: int,
    chunk_size: int,
    skip_daemon: bool,
) -> None:
    payload_b64 = base64.b64encode(local_path.read_bytes()).decode("ascii")
    ai2_exec_output(f": > {remote_path!r}.b64", wait_ms=wait_ms, skip_daemon=skip_daemon)
    for start in range(0, len(payload_b64), chunk_size):
        chunk = payload_b64[start : start + chunk_size]
        append_cmd = "python3 -c " + repr(
            "from pathlib import Path; "
            f"Path({remote_path!r} + '.b64').open('a', encoding='ascii').write({chunk!r})"
        )
        ai2_exec_output(append_cmd, wait_ms=wait_ms, skip_daemon=skip_daemon)
    decode_cmd = "python3 -c " + repr(
        "import base64; from pathlib import Path; "
        f"src=Path({remote_path!r} + '.b64'); "
        f"dst=Path({remote_path!r}); "
        "dst.parent.mkdir(parents=True, exist_ok=True); "
        "dst.write_bytes(base64.b64decode(src.read_text(encoding='ascii'))); "
        "print(dst.stat().st_size)"
    )
    size_output = ai2_exec_output(decode_cmd, wait_ms=wait_ms, skip_daemon=skip_daemon)
    expected_size = str(local_path.stat().st_size)
    if expected_size not in size_output:
        raise RuntimeError(
            f"Remote write size mismatch for {remote_path}: expected {expected_size}, got {size_output!r}"
        )


def main() -> int:
    args = parse_args()
    upload_file_b64_in_chunks(
        args.local_path.resolve(),
        args.remote_path,
        wait_ms=args.wait_ms,
        chunk_size=args.chunk_size,
        skip_daemon=args.skip_daemon,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "local_path": str(args.local_path.resolve()),
                "remote_path": args.remote_path,
                "bytes": args.local_path.stat().st_size,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

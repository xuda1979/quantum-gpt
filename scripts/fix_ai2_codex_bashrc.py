#!/usr/bin/env python3
"""Normalize Codex-related exports in ai2 /root/.bashrc."""

from __future__ import annotations

from pathlib import Path

TARGET = Path("/root/.bashrc")
REQUIRED_LINES = [
    "export LOCAL_CODEX_API_KEY=dummy",
    "export NO_PROXY=127.0.0.1,localhost",
    "export no_proxy=127.0.0.1,localhost",
    "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY",
    "export PATH=/root/.local/bin:/usr/local/bin:$PATH",
]


def main() -> int:
    lines = TARGET.read_text(encoding="utf-8").splitlines()
    filtered: list[str] = []
    for line in lines:
        if line in REQUIRED_LINES:
            continue
        if line.startswith("export PATH=/root/.local/bin:/usr/local/bin:"):
            continue
        filtered.append(line)
    if filtered and filtered[-1] != "":
        filtered.append("")
    filtered.extend(REQUIRED_LINES)
    TARGET.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    print(TARGET.read_text(encoding="utf-8").splitlines()[-8:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

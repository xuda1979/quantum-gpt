#!/usr/bin/env python3
"""Create a stricter code-first derivative of the fast-mini SFT split.

Normalizes assistant outputs by removing leading banner comments like
`# Solution`, `# Implementation`, or `# --- solution ---` while preserving
actual code content and the original chat structure.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BANNER_RE = re.compile(r"^#\s*(?:-+\s*)?(solution|implementation)(?:\s*-+)?\s*$", re.IGNORECASE)


def normalize_assistant_text(text: str) -> str:
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and BANNER_RE.match(lines[0].strip()):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def rewrite_split(src: Path, dst: Path) -> dict[str, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    changed = 0
    with src.open("r", encoding="utf-8") as in_f, dst.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            row = json.loads(line)
            total += 1
            before = row["messages"][-1]["content"]
            after = normalize_assistant_text(before)
            if after != before:
                changed += 1
                row["messages"][-1]["content"] = after
            out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"total": total, "changed": changed}


def main() -> int:
    base = Path("data/generated/fast-mini")
    out = Path("data/generated/fast-mini-codefirst")
    train_stats = rewrite_split(base / "train.jsonl", out / "train.jsonl")
    eval_stats = rewrite_split(base / "eval.jsonl", out / "eval.jsonl")
    print(json.dumps({"train": train_stats, "eval": eval_stats}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

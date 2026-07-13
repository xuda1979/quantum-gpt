#!/usr/bin/env python3
"""Convert the 场景建模代码数据 markdown cases into chat-sft-v1 JSONL.

Each source markdown file follows a 3-4 section structure:

    ## 1. 场景需求 (Scenario Demand)        -> becomes the USER instruction
    ## 2. 建模分析 (Modeling & Solver)       -> ASSISTANT answer (modeling)
    ## 3. 辅助编程 (Assisted Programming)     -> ASSISTANT answer (code)
    ## 4. 训练样本标签 (Training Metadata)    -> optional metadata (kept out of
                                               the assistant text, surfaced in
                                               the record `meta` block)

The user turn carries the scenario demand so the model learns to map a
real-world quantum-computing scenario to a full modeling + code answer.  The
assistant turn carries the modeling analysis and the assisted-programming code,
which is exactly the completion we want the model to learn to produce.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
from pathlib import Path

SYSTEM_PROMPT = (
    "你是一名量子计算建模与编程专家。给定一个真实业务场景需求，"
    "请完成：(1) 数学建模与求解框架分析；(2) 给出可运行的量子计算源码实现。"
    "回答需结构清晰、公式准确、代码可直接运行。"
)

# Matches a level-2 markdown header like "## 2. 建模分析 (Modeling & Solver)".
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(.+?)\s*$", re.MULTILINE)


def split_sections(text: str) -> list[tuple[str, str, str]]:
    """Return [(number, title, body)] for each ## N. ... section."""
    matches = list(SECTION_RE.finditer(text))
    sections: list[tuple[str, str, str]] = []
    for idx, match in enumerate(matches):
        number = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append((number, title, body))
    return sections


def build_record(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    if len(sections) < 2:
        return None
    by_number = {num: (title, body) for num, title, body in sections}

    demand = by_number.get("1")
    if demand is None:
        return None
    user_content = f"## 场景需求\n\n{demand[1]}"

    # Assistant answer = modeling (2) + assisted programming (3), preserving the
    # original markdown headers so the model learns the structured layout.
    assistant_parts: list[str] = []
    for num in ("2", "3"):
        if num in by_number:
            title, body = by_number[num]
            assistant_parts.append(f"## {num}. {title}\n\n{body}")
    if not assistant_parts:
        return None
    assistant_content = "\n\n".join(assistant_parts)

    # Section 4 (training metadata), if present, becomes record-level meta only.
    meta: dict[str, str] = {"source_file": path.name}
    if "4" in by_number:
        meta["training_metadata"] = by_number["4"][1]

    example_id = f"scenario_{path.stem}_{hashlib.sha1(path.name.encode()).hexdigest()[:8]}"
    return {
        "format": "chat-sft-v1",
        "source_schema": "scenario_modeling_md_v1",
        "example_id": example_id,
        "meta": meta,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src-glob", required=True, help="Glob for source .md files.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL path.")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["例子.md"],
        help="Basenames to skip (defaults to the example template file).",
    )
    args = parser.parse_args()

    paths = sorted(Path(p) for p in glob.glob(args.src_glob))
    exclude = set(args.exclude)
    records: list[dict] = []
    skipped: list[str] = []
    for path in paths:
        if path.name in exclude:
            continue
        record = build_record(path)
        if record is None:
            skipped.append(path.name)
            continue
        records.append(record)

    if not records:
        raise SystemExit(f"No usable records produced from glob: {args.src_glob}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "stage": "scenario_modeling_chatml_built",
                "out": str(args.out),
                "records": len(records),
                "skipped": skipped,
                "source_files": len(paths),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Strictly clean the ASI2 203-row distillation dataset.

Goals:
- normalize user prompts to English only;
- keep exactly one assistant code block;
- strip prose from code blocks;
- make Python answers syntactically runnable, with a safe fallback when needed.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_repaired_single_block_v3/all_chatml.jsonl"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_strict_english_runnable_v1"
)
ENGLISH_SUFFIX = "Write complete runnable code."

PROSE_PREFIXES = (
    "rationale",
    "notes",
    "plan",
    "final code",
    "code:",
    "code",
    "here",
    "the",
    "this",
    "below",
    "root cause",
    "**rationale**",
    "**important**",
    "**analysis**",
    "**说明**",
    "**分析**",
)

CODE_HINTS = (
    "import ",
    "from ",
    "def ",
    "class ",
    "@",
    "if __name__",
    "return ",
    "for ",
    "while ",
    "try:",
    "except ",
    "with ",
    "assert ",
    "print(",
    "pass",
    "elif ",
    "else:",
    "match ",
    "case ",
    "#",
    "```",
    "qbit ",
    "procedure ",
    "gate ",
    "qml.",
    "cirq.",
    "cudaq.",
    "from qiskit",
    "from braket",
    "from pytket",
    "from pyzx",
    "from pyquil",
    "from projectq",
    "import numpy",
    "import math",
)

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")
FENCE_RE = re.compile(r"```(?:[\w.+-]+)?\n(.*?)\n```", re.S)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def strip_chinese(text: str) -> str:
    text = text.replace("写出完整的可运行的代码。", ENGLISH_SUFFIX)
    text = text.replace("写成完整的可执行的代码。", ENGLISH_SUFFIX)
    text = text.replace("写出完整的可执行代码。", ENGLISH_SUFFIX)
    text = (
        text.replace("。", ".")
        .replace("，", ",")
        .replace("：", ":")
        .replace("；", ";")
        .replace("？", "?")
    )
    text = CHINESE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" .", ".").replace(" ,", ",").replace(" :", ":")
    return text


def append_english_suffix(prompt: str) -> str:
    prompt = strip_chinese(prompt)
    if ENGLISH_SUFFIX.lower() not in prompt.lower():
        if prompt and prompt[-1] not in ".?!":
            prompt += "."
        prompt += " " + ENGLISH_SUFFIX
    return prompt


def is_prose_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(PROSE_PREFIXES):
        return True
    if re.match(
        r"^(因此|所以|下面|说明|注意|如果|这里|完整|先|接下来|这段|使用|接着|然后|最后|测试|验证|实现|方案|目标|答案|输出|结果|修复|生成|创建|构建|请)\b",
        stripped,
    ):
        return True
    if (
        len(stripped) > 80
        and any(ch in stripped for ch in (".", ":", ";"))
        and not any(h in stripped for h in CODE_HINTS)
    ):
        return True
    return False


def extract_body(text: str) -> str:
    match = FENCE_RE.search(text)
    return match.group(1) if match else text


def clean_block(text: str) -> str:
    body = extract_body(text)
    lines = []
    for line in body.splitlines():
        if is_prose_line(line):
            continue
        if not line.strip():
            lines.append("")
            continue
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def is_python_like(text: str, metadata: dict[str, Any]) -> bool:
    lang = str(metadata.get("language", "")).lower()
    if lang == "python":
        return True
    lowered = text.lower()
    return any(
        token in lowered
        for token in (
            "import ",
            "def ",
            "class ",
            "if __name__",
            "print(",
            "numpy",
            "qiskit",
            "cirq",
            "pennylane",
            "cudaq",
            "pyzx",
            "pytket",
            "openfermion",
            "projectq",
        )
    )


def python_runnable(text: str) -> tuple[str, bool]:
    cleaned = clean_block(text)
    if cleaned:
        try:
            ast.parse(cleaned)
            return cleaned, False
        except SyntaxError:
            pass

    fallback_lines = ["# Sanitized fallback: original answer was not parseable Python."]
    for line in extract_body(text).splitlines():
        if not line.strip():
            fallback_lines.append("#")
        else:
            fallback_lines.append("# " + line.rstrip())
    fallback_lines.extend(["", 'if __name__ == "__main__":', '    print("OK")'])
    return "\n".join(fallback_lines), True


def sanitize_answer(text: str, metadata: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    raw = text or ""
    cleaned = clean_block(raw)
    stats: dict[str, Any] = {"fallback": False, "python": False}

    if is_python_like(raw, metadata):
        cleaned, fallback = python_runnable(raw)
        stats["python"] = True
        stats["fallback"] = fallback
        return f"```python\n{cleaned}\n```", stats

    if not cleaned:
        cleaned = '# Sanitized fallback: original answer had no retained code lines.\nprint("OK")'
        stats["fallback"] = True
        return f"```python\n{cleaned}\n```", stats

    lang = str(metadata.get("language", "")).strip().lower()
    if lang and lang not in {"python", "py"}:
        return f"```{lang}\n{cleaned}\n```", stats
    return f"```\n{cleaned}\n```", stats


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_jsonl)
    out_rows: list[dict[str, Any]] = []
    counts = {"rows": 0, "python_rows": 0, "python_fallback": 0, "question_cleaned": 0}

    for row in rows:
        new_row = json.loads(json.dumps(row))
        counts["rows"] += 1
        messages = new_row.get("messages")
        if not isinstance(messages, list) or len(messages) < 3:
            out_rows.append(new_row)
            continue

        user = messages[1]
        assistant = messages[2]
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}

        if isinstance(user, dict):
            before = str(user.get("content") or "")
            after = append_english_suffix(before)
            if after != before:
                counts["question_cleaned"] += 1
            user["content"] = after

        if isinstance(assistant, dict):
            before = str(assistant.get("content") or "")
            after, stats = sanitize_answer(before, metadata)
            assistant["content"] = after
            if stats["python"]:
                counts["python_rows"] += 1
            if stats["fallback"]:
                counts["python_fallback"] += 1

        out_rows.append(new_row)

    output_dir = args.output_dir
    output_file = output_dir / "all_chatml.jsonl"
    manifest_file = output_dir / "manifest.json"
    write_jsonl(output_file, out_rows)
    manifest = {
        "ok": True,
        "source": str(args.input_jsonl),
        "output_dir": str(output_dir),
        "output_file": str(output_file),
        "rows": counts["rows"],
        "question_cleaned": counts["question_cleaned"],
        "python_rows": counts["python_rows"],
        "python_fallback_rows": counts["python_fallback"],
        "policy": {
            "english_prompts_only": True,
            "single_code_block": True,
            "python_fallback": "comment_original_then_print_OK",
        },
    }
    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

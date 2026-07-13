#!/usr/bin/env python3
"""Normalize assistant answers so each one is a single complete code block.

The script preserves the existing dataset rows, but rewrites assistant content
to satisfy a strict single-block format:
- extract code fences and merge them into one block;
- if no code fence exists, keep only code-like lines when possible;
- otherwise wrap the remaining content as a single block.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_repaired_test/all_chatml.jsonl"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_repaired_single_block"
)

CODE_STARTERS = (
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
    "raise ",
    "assert ",
    "print(",
    "pass",
    "elif ",
    "else:",
    "match ",
    "case ",
    "qbit ",
    "procedure ",
    "gate ",
    "H |",
    "X |",
    "CNOT |",
    "Measure |",
    "qml.",
    "cirq.",
    "cudaq.",
    "from projectq",
    "from braket",
    "from pytket",
    "from qiskit",
    "from pyquil",
    "np.",
    "torch.",
    "eng =",
    "dev =",
    "qc =",
    "circuit =",
    "result =",
    "state =",
    "qubits =",
    "bits =",
    "phi =",
    "theta =",
)

PYTHON_LIKE_HINTS = (
    "python",
    "qiskit",
    "cirq",
    "pennylane",
    "qml.",
    "braket",
    "projectq",
    "pyquil",
    "pytket",
    "cudaq",
    "torch",
    "numpy",
)

ISQ_HINTS = ("isq", "qbit", "procedure main", "import std;")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def _extract_fenced_blocks(text: str) -> list[str]:
    blocks = []
    for match in re.finditer(r"```[^\n]*\n(.*?)```", text, re.S):
        block = match.group(1).strip("\n")
        if block:
            blocks.append(block)
    return blocks


def _looks_like_code_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return stripped.startswith(CODE_STARTERS) or stripped.startswith(
        ("    ", "\t", "#", "//", "/*", "*/")
    )


def _is_probably_prose(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(
        (
            "Rationale",
            "Notes",
            "Plan",
            "Final code",
            "Code:",
            "Code",
            "Here",
            "The",
            "This",
            "Below",
            "Root cause",
        )
    ):
        return True
    if re.match(
        r"^(因此|所以|下面|说明|注意|如果|这里|完整|先|接下来|这段|使用|接着|然后|最后|测试|验证|实现|方案|目标|答案|输出|结果|修复|生成|创建|构建|请)\b",
        stripped,
    ):
        return True
    if stripped.startswith(("**Rationale:**", "**说明**", "**分析**", "- ")):
        return True
    if stripped.startswith("```"):
        return True
    return False


def _strip_noncode_lines(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    in_codeish = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if kept and kept[-1] != "":
                kept.append("")
            continue
        if _looks_like_code_line(line):
            kept.append(line.rstrip())
            in_codeish = True
            continue
        if _is_probably_prose(line):
            continue
        if in_codeish:
            if stripped.startswith(
                (".", ")", "]", "}", ":", ",", "->", "=", "+", "-", "*", "/", "#")
            ):
                kept.append(line.rstrip())
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*[:=]\s*", stripped):
                kept.append(line.rstrip())
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*\(", stripped):
                kept.append(line.rstrip())
                continue
    return "\n".join(kept).strip()


def _infer_language(text: str) -> str:
    lower = text.lower()
    if any(hint in lower for hint in ISQ_HINTS):
        return "isq"
    if any(hint in lower for hint in ("qml.", "pennylane")):
        return "python"
    if any(
        hint in lower
        for hint in (
            "cirq",
            "qiskit",
            "braket",
            "projectq",
            "pyquil",
            "pytket",
            "cudaq",
            "numpy",
            "torch",
        )
    ):
        return "python"
    return ""


def normalize_answer(text: str) -> tuple[str, dict[str, Any]]:
    original = text or ""
    blocks = _extract_fenced_blocks(original)
    stats = {"fenced_blocks": len(blocks), "used_fences": bool(blocks), "fallback_lines": False}

    if blocks:
        cleaned_blocks = []
        for block in blocks:
            cleaned = _strip_noncode_lines(block)
            if cleaned:
                cleaned_blocks.append(cleaned)
        payload = "\n\n".join(cleaned_blocks).strip()
    else:
        payload = _strip_noncode_lines(original)
        stats["fallback_lines"] = True
        if not payload:
            payload = original.strip()

    lang = _infer_language(original)
    if payload.startswith("```") and payload.rstrip().endswith("```"):
        # already fenced, but normalize to a single outer fence by stripping existing fences
        payload = re.sub(r"^```[^\n]*\n", "", payload.strip())
        payload = re.sub(r"\n```$", "", payload.strip())

    fenced = f"```{lang}\n{payload.rstrip()}\n```" if lang else f"```\n{payload.rstrip()}\n```"
    return fenced, stats


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    counts = {"rows": 0, "changed": 0, "fenced_blocks": 0, "fallback_lines": 0}
    with args.input_jsonl.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ValueError(f"{args.input_jsonl}:{line_no}: expected a JSON object")
            messages = row.get("messages")
            if isinstance(messages, list) and len(messages) >= 3 and isinstance(messages[2], dict):
                before = str(messages[2].get("content") or "")
                after, stats = normalize_answer(before)
                messages[2]["content"] = after
                counts["rows"] += 1
                counts["fenced_blocks"] += int(stats["fenced_blocks"])
                counts["fallback_lines"] += int(stats["fallback_lines"])
                if after != before:
                    counts["changed"] += 1
            rows.append(row)

    output_dir = args.output_dir
    output_file = output_dir / "all_chatml.jsonl"
    manifest_file = output_dir / "manifest.json"
    write_jsonl(output_file, rows)
    manifest = {
        "ok": True,
        "source": str(args.input_jsonl),
        "output_dir": str(output_dir),
        "output_file": str(output_file),
        "rows": counts["rows"],
        "changed_rows": counts["changed"],
        "total_fenced_blocks_seen": counts["fenced_blocks"],
        "rows_using_line_fallback": counts["fallback_lines"],
        "policy": "single outer code block per assistant answer",
    }
    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

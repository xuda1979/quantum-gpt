#!/usr/bin/env python3
"""Filter distillation rows for quantum-coding and agentic-SE question quality."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/generated/quantum_distillation_teacher_responses_asi2_v1.jsonl")
DEFAULT_ACCEPTED = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality.jsonl"
)
DEFAULT_REJECTED = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_question_rejected.jsonl"
)
DEFAULT_REPORT = Path(
    "reports/quantum_distillation_teacher_responses_asi2_v1_question_quality.json"
)

LOW_VALUE_SOURCE_MARKERS = (
    "accessibility",
    "billing",
    "bibliography",
    "references",
    "changes.rst",
    "changelog",
    "common_issues",
    "common-issues",
)

CODING_MARKERS = (
    "implement",
    "write",
    "function",
    "class",
    "script",
    "code",
    "circuit",
    "simulat",
    "test",
    "pytest",
    "repair",
    "debug",
    "compile",
    "kernel",
    "operation",
    "api",
    "parser",
    "agent",
    "实现",
    "编写",
    "书写",
    "代码",
    "函数",
    "类",
    "脚本",
    "电路",
    "模拟",
    "测试",
    "修复",
    "调试",
    "编译",
    "算子",
)

QUANTUM_MARKERS = (
    "quantum",
    "qubit",
    "qiskit",
    "cirq",
    "pennylane",
    "braket",
    "pyquil",
    "pytket",
    "pyzx",
    "q#",
    "qsharp",
    "cuda-q",
    "cudaq",
    "mitiq",
    "qutip",
    "openfermion",
    "circuit",
    "pauli",
    "gate",
    "hamiltonian",
    "statevector",
    "量子",
    "比特",
    "电路",
    "泡利",
    "逻辑门",
    "哈密顿",
    "态矢量",
)

REPAIR_MARKERS = (
    "bug",
    "error",
    "failure",
    "fails",
    "fix",
    "repair",
    "incorrect",
    "traceback",
    "exception",
    "错误",
    "失败",
    "修复",
    "调试",
    "异常",
    "问题",
    "不正确",
)
AGENTIC_MARKERS = (
    "agent",
    "multi-turn",
    "log",
    "failure",
    "retry",
    "debug",
    "repair",
    "compile",
    "self-correct",
    "多轮",
    "日志",
    "失败",
    "重试",
    "修复",
    "自愈",
    "自我修复",
    "自纠",
    "编译",
)
OPTIMIZATION_MARKERS = (
    "optimize",
    "depth",
    "gate",
    "reduction",
    "transp",
    "layout",
    "density",
    "mapping",
    "efficient",
    "compress",
    "优化",
    "深度",
    "合并",
    "减少",
    "逻辑门",
    "转译",
    "映射",
    "效率",
    "拓扑",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--accepted-jsonl", type=Path, default=DEFAULT_ACCEPTED)
    parser.add_argument("--rejected-jsonl", type=Path, default=DEFAULT_REJECTED)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--min-accepted", type=int, default=1)
    return parser.parse_args()


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be object")
            yield line_no, row


def has_any(text: str, markers: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in markers)


def count_words(text: str) -> int:
    import re

    text_clean = text.strip()
    if not text_clean:
        return 0
    chinese_char_count = len(re.findall(r"[\u4e00-\u9fff]", text_clean))
    english_part = re.sub(r"[\u4e00-\u9fff]", " ", text_clean)
    english_word_count = len(english_part.split())
    return chinese_char_count + english_word_count


def rejection_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    source_path = str(metadata.get("source_path", ""))
    source_title = str(metadata.get("source_title", ""))
    source_text = f"{source_path}\n{source_title}".lower()
    instruction = str(row.get("instruction", ""))
    response = str(row.get("response", ""))
    task_type = str(row.get("task_type", ""))
    combined = f"{instruction}\n{response}"

    if has_any(source_text, LOW_VALUE_SOURCE_MARKERS):
        reasons.append("low_value_source_doc")
    if not has_any(combined, CODING_MARKERS):
        reasons.append("missing_coding_task_shape")
    if not has_any(combined, QUANTUM_MARKERS):
        reasons.append("missing_quantum_task_shape")
    if task_type == "repair" and not has_any(combined, REPAIR_MARKERS):
        reasons.append("repair_without_failure_signal")
    if task_type == "agentic_trajectory" and not has_any(combined, AGENTIC_MARKERS):
        reasons.append("agentic_without_agent_failure_signal")
    if task_type == "optimization" and not has_any(combined, OPTIMIZATION_MARKERS):
        reasons.append("optimization_without_optimization_signal")
    if count_words(instruction) < 20:
        reasons.append("instruction_too_short_for_distillation")
    return reasons


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    total = 0

    for _line_no, row in iter_rows(args.input_jsonl):
        total += 1
        reasons = rejection_reasons(row)
        if reasons:
            rejected_row = dict(row)
            metadata = dict(
                rejected_row.get("metadata")
                if isinstance(rejected_row.get("metadata"), dict)
                else {}
            )
            metadata["question_quality_reject_reasons"] = reasons
            rejected_row["metadata"] = metadata
            rejected.append(rejected_row)
            reason_counts.update(reasons)
        else:
            accepted.append(row)

    write_jsonl(args.accepted_jsonl, accepted)
    write_jsonl(args.rejected_jsonl, rejected)
    report = {
        "ok": len(accepted) >= args.min_accepted,
        "input_jsonl": str(args.input_jsonl.resolve()),
        "accepted_jsonl": str(args.accepted_jsonl.resolve()),
        "rejected_jsonl": str(args.rejected_jsonl.resolve()),
        "total_rows": total,
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
        "min_accepted": args.min_accepted,
        "reason_counts": dict(sorted(reason_counts.items())),
        "policy": {
            "target": "quantum coding plus agentic software engineering",
            "reject_low_value_source_markers": list(LOW_VALUE_SOURCE_MARKERS),
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

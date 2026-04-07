#!/usr/bin/env python3
"""Heuristic summary for base-vs-adapter qualitative eval reports."""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


CODE_STARTERS = ("def ", "class ", "import ", "from ", "@", "if ", "for ", "while ", "try:", "#")
ANCHOR_TOKENS = (
    "session_id",
    "active_window",
    "ts",
    "kind",
    "type",
    "timestamp",
    "history",
    "message_counts",
    "timeline",
    "q0",
    "q1",
    "bitstring",
    "pauli",
    "gates",
)


@dataclass
class OutputSummary:
    name: str
    code_fence: bool
    starts_like_code: bool
    syntax_ok: bool
    required_names_present: list[str]
    missing_required_names: list[str]
    reference_keys_present: list[str]
    missing_reference_keys: list[str]
    anchor_hits: list[str]
    suspicious_anchor_hits: list[str]
    line_count: int
    char_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_json", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of markdown.")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_required_names(prompt: str) -> list[str]:
    names: list[str] = []
    for pattern in (r"- Required function: def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", r"- Required class:\s*([A-Za-z_][A-Za-z0-9_]*)"):
        names.extend(re.findall(pattern, prompt))
    return names


def extract_reference_keys(reference: str) -> list[str]:
    keys = set(re.findall(r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*[:\]]', reference))
    return sorted(keys)


def normalize_output(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def starts_like_code(text: str) -> bool:
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        return candidate.startswith(CODE_STARTERS)
    return False


def syntax_ok(text: str) -> bool:
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def summarize_output(name: str, output: str, required_names: list[str], reference_keys: list[str]) -> OutputSummary:
    normalized = normalize_output(output)
    present_required = [item for item in required_names if re.search(rf"\b{re.escape(item)}\b", normalized)]
    present_reference = [item for item in reference_keys if re.search(rf'["\']{re.escape(item)}["\']', normalized)]
    anchor_hits = [item for item in ANCHOR_TOKENS if re.search(rf"\b{re.escape(item)}\b", normalized)]

    suspicious = []
    if "ts" in reference_keys and "timestamp" in anchor_hits and "timestamp" not in reference_keys:
        suspicious.append("timestamp_without_ts_contract")
    if "type" in reference_keys and "kind" in anchor_hits and "kind" not in reference_keys:
        suspicious.append("kind_without_type_contract")
    if "kind" in reference_keys and "type" in anchor_hits and "type" not in reference_keys:
        suspicious.append("type_without_kind_contract")
    if "history" not in reference_keys and "history" in anchor_hits:
        suspicious.append("history_hallucination")

    return OutputSummary(
        name=name,
        code_fence="```" in output,
        starts_like_code=starts_like_code(normalized),
        syntax_ok=syntax_ok(normalized),
        required_names_present=present_required,
        missing_required_names=[item for item in required_names if item not in present_required],
        reference_keys_present=present_reference,
        missing_reference_keys=[item for item in reference_keys if item not in present_reference],
        anchor_hits=anchor_hits,
        suspicious_anchor_hits=suspicious,
        line_count=len([line for line in normalized.splitlines() if line.strip()]),
        char_count=len(normalized),
    )


def aggregate(examples: list[dict], side: str) -> dict:
    summaries = [example[f"{side}_summary"] for example in examples]
    total = len(summaries)
    return {
        "total_examples": total,
        "syntax_ok": sum(item["syntax_ok"] for item in summaries),
        "starts_like_code": sum(item["starts_like_code"] for item in summaries),
        "code_fence": sum(item["code_fence"] for item in summaries),
        "all_required_names_present": sum(not item["missing_required_names"] for item in summaries),
        "any_suspicious_anchor_hits": sum(bool(item["suspicious_anchor_hits"]) for item in summaries),
        "avg_reference_key_hits": round(
            sum(len(item["reference_keys_present"]) for item in summaries) / max(total, 1), 2
        ),
    }


def build_summary(report: dict) -> dict:
    examples = []
    for example in report["examples"]:
        required_names = extract_required_names(example["prompt"])
        reference_keys = extract_reference_keys(example.get("reference", ""))
        base_summary = summarize_output("base", example.get("base_output", ""), required_names, reference_keys)
        adapter_summary = summarize_output("adapter", example.get("adapter_output", ""), required_names, reference_keys)
        examples.append(
            {
                "example_id": example["example_id"],
                "task_id": example.get("task_id"),
                "task_name": example.get("task_name"),
                "domain": example.get("domain"),
                "required_names": required_names,
                "reference_keys": reference_keys,
                "base_summary": asdict(base_summary),
                "adapter_summary": asdict(adapter_summary),
            }
        )

    return {
        "report_json": report,
        "aggregate": {
            "base": aggregate(examples, "base"),
            "adapter": aggregate(examples, "adapter"),
        },
        "examples": examples,
    }


def to_markdown(summary: dict, report_path: Path) -> str:
    lines = [f"# Qualitative Summary: {report_path}", ""]
    for side in ("base", "adapter"):
        agg = summary["aggregate"][side]
        lines.extend(
            [
                f"## {side}",
                f"- total_examples: `{agg['total_examples']}`",
                f"- syntax_ok: `{agg['syntax_ok']}`",
                f"- starts_like_code: `{agg['starts_like_code']}`",
                f"- code_fence: `{agg['code_fence']}`",
                f"- all_required_names_present: `{agg['all_required_names_present']}`",
                f"- any_suspicious_anchor_hits: `{agg['any_suspicious_anchor_hits']}`",
                f"- avg_reference_key_hits: `{agg['avg_reference_key_hits']}`",
                "",
            ]
        )

    lines.append("## Per Example")
    for example in summary["examples"]:
        lines.append(f"- `{example['example_id']}` / `{example['task_id']}`")
        lines.append(f"  required_names: `{', '.join(example['required_names']) or '-'}`")
        for side in ("base", "adapter"):
            item = example[f"{side}_summary"]
            lines.append(
                "  "
                + f"{side}: syntax_ok={item['syntax_ok']}, starts_like_code={item['starts_like_code']}, "
                + f"code_fence={item['code_fence']}, missing_required={item['missing_required_names'] or '[]'}, "
                + f"suspicious={item['suspicious_anchor_hits'] or '[]'}"
            )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = load_json(args.report_json)
    summary = build_summary(report)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(summary, args.report_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

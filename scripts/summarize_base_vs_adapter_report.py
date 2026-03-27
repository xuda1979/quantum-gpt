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
    code_fence_closed: bool
    starts_like_code: bool
    syntax_ok: bool
    parse_error: str | None
    required_names_present: list[str]
    missing_required_names: list[str]
    reference_keys_present: list[str]
    missing_reference_keys: list[str]
    anchor_hits: list[str]
    suspicious_anchor_hits: list[str]
    first_nonempty_line: str
    line_count: int
    char_count: int
    score: int
    score_breakdown: dict[str, int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_json", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of markdown.")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_top_level_symbols(reference: str) -> list[str]:
    try:
        tree = ast.parse(reference)
    except SyntaxError:
        return []

    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
    return names


def extract_required_names(prompt: str, reference: str) -> list[str]:
    names: list[str] = []
    for pattern in (r"- Required function: def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", r"- Required class:\s*([A-Za-z_][A-Za-z0-9_]*)"):
        names.extend(re.findall(pattern, prompt))
    if names:
        return names
    return extract_top_level_symbols(reference)


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


def detect_code_fence(text: str) -> tuple[bool, bool]:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return False, False
    fence_count = stripped.count("```")
    return True, fence_count >= 2 and stripped.endswith("```")


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


def get_parse_error(text: str) -> str | None:
    try:
        ast.parse(text)
        return None
    except SyntaxError as exc:
        return f"{exc.msg} (line {exc.lineno}, col {exc.offset})"


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        candidate = line.strip()
        if candidate:
            return candidate
    return ""


def compute_score(
    syntax_is_ok: bool,
    starts_as_code: bool,
    code_fence_closed: bool,
    missing_required_names: list[str],
    reference_keys_present: list[str],
    suspicious_anchor_hits: list[str],
) -> tuple[int, dict[str, int]]:
    breakdown = {
        "syntax_ok": 3 if syntax_is_ok else 0,
        "starts_like_code": 1 if starts_as_code else 0,
        "closed_code_fence": 1 if code_fence_closed else 0,
        "all_required_names_present": 2 if not missing_required_names else 0,
        "reference_key_hits": len(reference_keys_present),
        "suspicious_anchor_penalty": -len(suspicious_anchor_hits),
    }
    return sum(breakdown.values()), breakdown


def summarize_output(name: str, output: str, required_names: list[str], reference_keys: list[str]) -> OutputSummary:
    normalized = normalize_output(output)
    code_fence, code_fence_closed = detect_code_fence(output)
    syntax_is_ok = syntax_ok(normalized)
    parse_error = get_parse_error(normalized)
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

    score, score_breakdown = compute_score(
        syntax_is_ok=syntax_is_ok,
        starts_as_code=starts_like_code(normalized),
        code_fence_closed=code_fence_closed,
        missing_required_names=[item for item in required_names if item not in present_required],
        reference_keys_present=present_reference,
        suspicious_anchor_hits=suspicious,
    )

    return OutputSummary(
        name=name,
        code_fence=code_fence,
        code_fence_closed=code_fence_closed,
        starts_like_code=starts_like_code(normalized),
        syntax_ok=syntax_is_ok,
        parse_error=parse_error,
        required_names_present=present_required,
        missing_required_names=[item for item in required_names if item not in present_required],
        reference_keys_present=present_reference,
        missing_reference_keys=[item for item in reference_keys if item not in present_reference],
        anchor_hits=anchor_hits,
        suspicious_anchor_hits=suspicious,
        first_nonempty_line=first_nonempty_line(normalized),
        line_count=len([line for line in normalized.splitlines() if line.strip()]),
        char_count=len(normalized),
        score=score,
        score_breakdown=score_breakdown,
    )


def aggregate(examples: list[dict], side: str) -> dict:
    summaries = [example[f"{side}_summary"] for example in examples]
    total = len(summaries)
    return {
        "total_examples": total,
        "syntax_ok": sum(item["syntax_ok"] for item in summaries),
        "starts_like_code": sum(item["starts_like_code"] for item in summaries),
        "code_fence": sum(item["code_fence"] for item in summaries),
        "code_fence_closed": sum(item["code_fence_closed"] for item in summaries),
        "all_required_names_present": sum(not item["missing_required_names"] for item in summaries),
        "any_suspicious_anchor_hits": sum(bool(item["suspicious_anchor_hits"]) for item in summaries),
        "avg_reference_key_hits": round(
            sum(len(item["reference_keys_present"]) for item in summaries) / max(total, 1), 2
        ),
        "avg_score": round(sum(item["score"] for item in summaries) / max(total, 1), 2),
    }


def aggregate_delta(base_agg: dict, adapter_agg: dict) -> dict:
    fields = (
        "syntax_ok",
        "starts_like_code",
        "code_fence",
        "code_fence_closed",
        "all_required_names_present",
        "any_suspicious_anchor_hits",
        "avg_reference_key_hits",
        "avg_score",
    )
    return {f"{field}_delta": round(adapter_agg[field] - base_agg[field], 2) for field in fields}


def compare_example(base_summary: dict, adapter_summary: dict) -> dict:
    base_score = base_summary["score"]
    adapter_score = adapter_summary["score"]
    if adapter_score > base_score:
        winner = "adapter"
    elif base_score > adapter_score:
        winner = "base"
    else:
        winner = "tie"

    return {
        "winner": winner,
        "score_delta": adapter_score - base_score,
        "base_score": base_score,
        "adapter_score": adapter_score,
    }


def aggregate_wins(examples: list[dict]) -> dict:
    wins = {"adapter": 0, "base": 0, "tie": 0}
    for example in examples:
        wins[example["comparison"]["winner"]] += 1
    return wins


def group_examples_by_domain(examples: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for example in examples:
        groups.setdefault(example.get("domain") or "unknown", []).append(example)
    return groups


def build_summary(report: dict) -> dict:
    examples = []
    for example in report["examples"]:
        required_names = extract_required_names(example["prompt"], example.get("reference", ""))
        reference_keys = extract_reference_keys(example.get("reference", ""))
        base_summary = summarize_output("base", example.get("base_output", ""), required_names, reference_keys)
        adapter_summary = summarize_output("adapter", example.get("adapter_output", ""), required_names, reference_keys)
        comparison = compare_example(asdict(base_summary), asdict(adapter_summary))
        examples.append(
            {
                "example_id": example["example_id"],
                "task_id": example.get("task_id"),
                "task_name": example.get("task_name"),
                "domain": example.get("domain"),
                "prompt_variant": example.get("prompt_variant"),
                "review_checklist": example.get("review_checklist", []),
                "required_names": required_names,
                "reference_keys": reference_keys,
                "base_summary": asdict(base_summary),
                "adapter_summary": asdict(adapter_summary),
                "comparison": comparison,
            }
        )

    base_agg = aggregate(examples, "base")
    adapter_agg = aggregate(examples, "adapter")
    by_domain = {}
    for domain, domain_examples in group_examples_by_domain(examples).items():
        domain_base = aggregate(domain_examples, "base")
        domain_adapter = aggregate(domain_examples, "adapter")
        by_domain[domain] = {
            "base": domain_base,
            "adapter": domain_adapter,
            "delta": aggregate_delta(domain_base, domain_adapter),
            "wins": aggregate_wins(domain_examples),
        }

    return {
        "report_json": report,
        "aggregate": {
            "base": base_agg,
            "adapter": adapter_agg,
            "delta": aggregate_delta(base_agg, adapter_agg),
            "wins": aggregate_wins(examples),
        },
        "by_domain": by_domain,
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
                f"- code_fence_closed: `{agg['code_fence_closed']}`",
                f"- all_required_names_present: `{agg['all_required_names_present']}`",
                f"- any_suspicious_anchor_hits: `{agg['any_suspicious_anchor_hits']}`",
                f"- avg_reference_key_hits: `{agg['avg_reference_key_hits']}`",
                f"- avg_score: `{agg['avg_score']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Delta",
            f"- syntax_ok_delta: `{summary['aggregate']['delta']['syntax_ok_delta']}`",
            f"- starts_like_code_delta: `{summary['aggregate']['delta']['starts_like_code_delta']}`",
            f"- code_fence_closed_delta: `{summary['aggregate']['delta']['code_fence_closed_delta']}`",
            f"- all_required_names_present_delta: `{summary['aggregate']['delta']['all_required_names_present_delta']}`",
            f"- any_suspicious_anchor_hits_delta: `{summary['aggregate']['delta']['any_suspicious_anchor_hits_delta']}`",
            f"- avg_reference_key_hits_delta: `{summary['aggregate']['delta']['avg_reference_key_hits_delta']}`",
            f"- avg_score_delta: `{summary['aggregate']['delta']['avg_score_delta']}`",
            f"- wins: `adapter={summary['aggregate']['wins']['adapter']}, base={summary['aggregate']['wins']['base']}, tie={summary['aggregate']['wins']['tie']}`",
            "",
        ]
    )

    lines.append("## By Domain")
    for domain, domain_summary in sorted(summary["by_domain"].items()):
        lines.append(f"- `{domain}`: adapter_wins={domain_summary['wins']['adapter']}, base_wins={domain_summary['wins']['base']}, tie={domain_summary['wins']['tie']}, avg_score_delta={domain_summary['delta']['avg_score_delta']}")
    lines.append("")

    lines.append("## Per Example")
    for example in summary["examples"]:
        lines.append(
            f"- `{example['example_id']}` / `{example['task_id']}` / domain=`{example.get('domain')}` / winner=`{example['comparison']['winner']}` / score_delta=`{example['comparison']['score_delta']}`"
        )
        lines.append(f"  prompt_variant: `{example.get('prompt_variant') or '-'}`")
        lines.append(f"  required_names: `{', '.join(example['required_names']) or '-'}`")
        for side in ("base", "adapter"):
            item = example[f"{side}_summary"]
            lines.append(
                "  "
                + f"{side}: score={item['score']}, syntax_ok={item['syntax_ok']}, starts_like_code={item['starts_like_code']}, "
                + f"code_fence={item['code_fence']}, code_fence_closed={item['code_fence_closed']}, "
                + f"missing_required={item['missing_required_names'] or '[]'}, suspicious={item['suspicious_anchor_hits'] or '[]'}"
            )
            if item["parse_error"]:
                lines.append("  " + f"{side}_parse_error: `{item['parse_error']}`")
            lines.append("  " + f"{side}_first_line: `{item['first_nonempty_line'][:100]}`")
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

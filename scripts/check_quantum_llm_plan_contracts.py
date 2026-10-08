#!/usr/bin/env python3
"""Check lightweight plan contracts for quantum LLM eval records.

The integrated plan calls for early gates around numeric-boundary safety,
answer provenance, and parseable structured outputs. This script intentionally
keeps those checks format-tolerant: it accepts JSONL datasets, JSON candidate
output files, and plain-text candidate files, then reports only the contracts it
can observe.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NUMERIC_BOUNDARY_MARKERS = {
    "numeric_boundary",
    "numeric_boundaries",
    "numeric_boundary_case",
    "numeric_boundary_cases",
    "numerical_boundary",
    "numerical_boundary_case",
    "boundary_safety",
    "boundary_case",
    "boundary_cases",
    "boundary_condition",
    "boundary_conditions",
    "edge_case",
    "edge_cases",
    "off_by_one",
    "off_by_one_case",
}

NUMERIC_BOUNDARY_SIGNAL_RE = re.compile(
    r"\b("
    r"numeric(?:al)?[-_\s]+boundar(?:y|ies)|"
    r"boundary[-_\s]+condition(?:s)?|"
    r"boundary[-_\s]+case(?:s)?|"
    r"edge[-_\s]+case(?:s)?|"
    r"off[-_\s]+by[-_\s]+one|"
    r"inclusive|exclusive|"
    r"lower[-_\s]+bound|upper[-_\s]+bound|"
    r"min(?:imum)?|max(?:imum)?|"
    r"zero|negative|overflow|underflow|clamp(?:ing)?|round(?:ing)?"
    r")\b",
    re.IGNORECASE,
)
NUMERIC_TOKEN_RE = re.compile(
    r"[-+]?\d+(?:\.\d+)?|\bzero\b|\bone\b|\btwo\b|\bmin\b|\bmax\b", re.IGNORECASE
)

ANSWER_KEYS = {
    "answer",
    "assistant",
    "candidate",
    "candidate_answer",
    "candidate_text",
    "completion",
    "final_answer",
    "model_answer",
    "output",
    "response",
}

TOOL_KEYS = {
    "external_tool_result",
    "external_tool_results",
    "observation",
    "observations",
    "rag_context",
    "retrieval_context",
    "retrieval_result",
    "retrieval_results",
    "tool_call",
    "tool_calls",
    "tool_output",
    "tool_outputs",
    "tool_result",
    "tool_results",
}

MODEL_FIELD_KEYS = {
    "generated_code",
    "generated_text",
    "model_generated",
    "model_generated_code",
    "model_generated_text",
    "model_output",
}

IR_KEYS = {
    "ir",
    "plan_ir",
    "program_ir",
    "quantum_ir",
    "structured_ir",
    "structured_output",
}

TOOL_TEXT_RE = re.compile(
    r"(<tool_result>|</tool_result>|\bexternal\s+tool\b|\btool\s+result\b|\bretrieval\s+result\b|\bretrieved\s+context\b|\bobservation\b)",
    re.IGNORECASE,
)
MODEL_TEXT_RE = re.compile(
    r"(<model_generated>|</model_generated>|\bmodel[-_\s]+generated\b|\bmodel\s+output\b|\bgenerated\s+(?:code|text|answer)\b)",
    re.IGNORECASE,
)


def normalize_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def marker_value_is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return normalize_token(value) not in {"", "0", "false", "no", "none", "null"}
    return is_non_empty(value)


def load_records(path: Path) -> tuple[list[dict[str, Any]], list[str], str]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return [], [f"{path} is empty"], "empty"

    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        errors: list[str] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_no} invalid JSON: {exc}")
                continue
            records.append(as_record(parsed, line_no=line_no))
        return records, errors, "jsonl"

    if stripped[0] in "[{":
        try:
            parsed_json = json.loads(stripped)
        except json.JSONDecodeError as exc:
            return [], [f"{path} invalid JSON: {exc}"], "json"
        return records_from_json(parsed_json), [], "json"

    return [{"_record_index": 1, "_plain_text": text, "candidate_text": text}], [], "plain_text"


def records_from_json(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [as_record(item, line_no=index) for index, item in enumerate(value, start=1)]
    if isinstance(value, dict):
        for key in ("records", "rows", "examples", "outputs", "candidates"):
            nested = value.get(key)
            if isinstance(nested, list):
                return [
                    as_record(item, line_no=index) for index, item in enumerate(nested, start=1)
                ]
        return [as_record(value, line_no=1)]
    return [as_record(value, line_no=1)]


def as_record(value: Any, *, line_no: int) -> dict[str, Any]:
    if isinstance(value, dict):
        record = dict(value)
    else:
        record = {"value": value}
    record.setdefault("_record_index", line_no)
    return record


def record_id(record: dict[str, Any]) -> str:
    metadata = record.get("metadata")
    candidates = [
        record.get("example_id"),
        record.get("id"),
        record.get("task_id"),
        metadata.get("example_id") if isinstance(metadata, dict) else None,
        metadata.get("task_id") if isinstance(metadata, dict) else None,
        record.get("_record_index"),
    ]
    for candidate in candidates:
        if candidate is not None and str(candidate).strip():
            return str(candidate)
    return "unknown"


def iter_paths(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, key, nested
            yield from iter_paths(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]"
            yield path, str(index), nested
            yield from iter_paths(nested, path)


def collect_text(value: Any) -> str:
    chunks: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, str):
            chunks.append(item)
        elif isinstance(item, dict):
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return "\n".join(chunks)


def has_numeric_boundary_marker(record: dict[str, Any]) -> bool:
    tags = record.get("tags")
    if isinstance(tags, list):
        for tag in tags:
            if normalize_token(tag) in NUMERIC_BOUNDARY_MARKERS:
                return True

    labels = record.get("labels")
    if isinstance(labels, list):
        for label in labels:
            if normalize_token(label) in NUMERIC_BOUNDARY_MARKERS:
                return True

    for _path, key, value in iter_paths(record):
        normalized_key = normalize_token(key)
        if normalized_key in NUMERIC_BOUNDARY_MARKERS and marker_value_is_true(value):
            return True
        if isinstance(value, str) and normalized_key in {
            "contract",
            "contracts",
            "eval_contract",
            "eval_contracts",
        }:
            if normalize_token(value) in NUMERIC_BOUNDARY_MARKERS:
                return True
        if isinstance(value, list) and normalized_key in {"contracts", "eval_contracts"}:
            if any(normalize_token(item) in NUMERIC_BOUNDARY_MARKERS for item in value):
                return True

    return False


def looks_like_numeric_boundary_case(record: dict[str, Any]) -> bool:
    if has_numeric_boundary_marker(record):
        return True
    text = collect_text(
        {
            key: record.get(key)
            for key in (
                "instruction",
                "prompt",
                "question",
                "response",
                "answer",
                "candidate",
                "candidate_text",
                "output",
                "completion",
                "messages",
                "metadata",
            )
            if key in record
        }
    )
    return bool(NUMERIC_BOUNDARY_SIGNAL_RE.search(text) and NUMERIC_TOKEN_RE.search(text))


def has_candidate_answer(record: dict[str, Any]) -> bool:
    for _path, key, value in iter_paths(record):
        if normalize_token(key) in ANSWER_KEYS | MODEL_FIELD_KEYS and is_non_empty(value):
            return True
    messages = record.get("messages")
    if isinstance(messages, list):
        return any(
            isinstance(msg, dict)
            and msg.get("role") == "assistant"
            and is_non_empty(msg.get("content"))
            for msg in messages
        )
    for key in ("answer_parts", "output_parts", "segments"):
        parts = record.get(key)
        if isinstance(parts, list):
            for part in parts:
                if not isinstance(part, dict):
                    continue
                raw_source = (
                    part.get("source")
                    or part.get("provenance")
                    or part.get("origin")
                    or part.get("type")
                    or part.get("role")
                )
                if normalize_token(raw_source) in {
                    "assistant",
                    "model",
                    "model_generated",
                    "generated",
                    "candidate",
                }:
                    return True
    return False


def has_external_tool_material(record: dict[str, Any]) -> bool:
    for _path, key, value in iter_paths(record):
        if normalize_token(key) in TOOL_KEYS and is_non_empty(value):
            return True
    for key in ("answer_parts", "output_parts", "segments", "messages"):
        parts = record.get(key)
        if isinstance(parts, list):
            for part in parts:
                if not isinstance(part, dict):
                    continue
                raw_source = (
                    part.get("source")
                    or part.get("provenance")
                    or part.get("origin")
                    or part.get("type")
                    or part.get("role")
                )
                if normalize_token(raw_source) in {
                    "tool",
                    "tool_result",
                    "external_tool",
                    "retrieval",
                    "observation",
                }:
                    return True
    return bool(TOOL_TEXT_RE.search(collect_text(record)))


def has_structured_segment_provenance(record: dict[str, Any]) -> bool:
    for key in ("answer_parts", "output_parts", "segments", "messages"):
        parts = record.get(key)
        if not isinstance(parts, list):
            continue
        sources: set[str] = set()
        saw_unlabeled = False
        for part in parts:
            if not isinstance(part, dict):
                continue
            raw_source = (
                part.get("source")
                or part.get("provenance")
                or part.get("origin")
                or part.get("type")
                or part.get("role")
            )
            normalized = normalize_token(raw_source)
            if normalized in {"tool", "tool_result", "external_tool", "retrieval", "observation"}:
                sources.add("tool")
            elif normalized in {"assistant", "model", "model_generated", "generated", "candidate"}:
                sources.add("model")
            elif is_non_empty(part.get("content")):
                saw_unlabeled = True
        if {"tool", "model"} <= sources and not saw_unlabeled:
            return True
    return False


def has_separate_provenance_fields(record: dict[str, Any]) -> bool:
    saw_tool = False
    saw_model = False
    for _path, key, value in iter_paths(record):
        normalized = normalize_token(key)
        if normalized in TOOL_KEYS and is_non_empty(value):
            saw_tool = True
        if normalized in MODEL_FIELD_KEYS and is_non_empty(value):
            saw_model = True
    return saw_tool and saw_model


def has_textual_provenance_markers(record: dict[str, Any]) -> bool:
    text = collect_text(record)
    return bool(TOOL_TEXT_RE.search(text) and MODEL_TEXT_RE.search(text))


def provenance_is_distinguished(record: dict[str, Any]) -> bool:
    if has_structured_segment_provenance(record):
        return True
    if has_separate_provenance_fields(record):
        return True

    # Separate external tool fields plus a normal answer field are acceptable:
    # the record stores tool material out-of-band instead of blending it into
    # generated prose/code.
    if has_external_tool_material(record) and has_candidate_answer(record):
        for _path, key, value in iter_paths(record):
            if normalize_token(key) in TOOL_KEYS and is_non_empty(value):
                return True

    return has_textual_provenance_markers(record)


def iter_ir_values(record: dict[str, Any]):
    for path, key, value in iter_paths(record):
        if normalize_token(key) in IR_KEYS and is_non_empty(value):
            yield path, value

    text = record.get("_plain_text")
    if isinstance(text, str):
        for match in re.finditer(
            r"<structured_ir>\s*(.*?)\s*</structured_ir>", text, flags=re.IGNORECASE | re.DOTALL
        ):
            yield "_plain_text.<structured_ir>", match.group(1)
        for match in re.finditer(
            r"```(?:json|ir)?\s*(\{.*?\}|\[.*?\])\s*```", text, flags=re.IGNORECASE | re.DOTALL
        ):
            candidate = match.group(1)
            if any(token in candidate for token in ('"ir"', '"steps"', '"operations"', '"nodes"')):
                yield "_plain_text.fenced_json", candidate


def parse_ir_value(value: Any) -> tuple[bool, str | None]:
    if isinstance(value, (dict, list)):
        return True, None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json|ir)?\s*", "", stripped, flags=re.IGNORECASE)
            stripped = re.sub(r"\s*```$", "", stripped)
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            return False, str(exc)
        if not isinstance(parsed, (dict, list)):
            return False, "IR must parse to a JSON object or array"
        return True, None
    return False, f"IR value has unsupported type {type(value).__name__}"


def check_records(
    records: list[dict[str, Any]], load_errors: list[str], input_path: Path, input_kind: str
) -> dict[str, Any]:
    numeric_candidates: list[dict[str, Any]] = []
    missing_numeric_markers: list[dict[str, Any]] = []
    provenance_applicable: list[dict[str, Any]] = []
    provenance_failures: list[dict[str, Any]] = []
    ir_present: list[dict[str, Any]] = []
    ir_failures: list[dict[str, Any]] = []

    for record in records:
        rid = record_id(record)

        numeric_signal = looks_like_numeric_boundary_case(record)
        numeric_marked = has_numeric_boundary_marker(record)
        if numeric_signal:
            numeric_candidates.append({"record_id": rid, "marked": numeric_marked})
            if not numeric_marked:
                missing_numeric_markers.append(
                    {"record_id": rid, "reason": "numeric-boundary signal without marker"}
                )

        tool_material = has_external_tool_material(record)
        answer_material = has_candidate_answer(record)
        if tool_material and answer_material:
            distinguished = provenance_is_distinguished(record)
            provenance_applicable.append({"record_id": rid, "distinguished": distinguished})
            if not distinguished:
                provenance_failures.append(
                    {
                        "record_id": rid,
                        "reason": "external tool material and candidate/model answer are not separated by fields, segments, or text markers",
                    }
                )

        for ir_path, ir_value in iter_ir_values(record):
            parseable, error = parse_ir_value(ir_value)
            ir_present.append({"record_id": rid, "path": ir_path, "parseable": parseable})
            if not parseable:
                ir_failures.append({"record_id": rid, "path": ir_path, "error": error})

    checks = {
        "no_load_errors": not load_errors,
        "numeric_boundary_marking_ok": not missing_numeric_markers,
        "provenance_contract_ok": not provenance_failures,
        "structured_ir_parseability_ok": not ir_failures,
    }

    report: dict[str, Any] = {
        "input": str(input_path.resolve()),
        "input_kind": input_kind,
        "records_total": len(records),
        "ok": all(checks.values()),
        "checks": checks,
        "numeric_boundary": {
            "records_with_signal": len(numeric_candidates),
            "records_marked": sum(1 for item in numeric_candidates if item["marked"]),
            "missing_marker_count": len(missing_numeric_markers),
            "missing_markers": missing_numeric_markers,
        },
        "provenance": {
            "records_requiring_distinction": len(provenance_applicable),
            "distinguished_count": sum(
                1 for item in provenance_applicable if item["distinguished"]
            ),
            "failure_count": len(provenance_failures),
            "failures": provenance_failures,
        },
        "structured_ir": {
            "present_count": len(ir_present),
            "parseable_count": sum(1 for item in ir_present if item["parseable"]),
            "failure_count": len(ir_failures),
            "failures": ir_failures,
        },
        "errors": load_errors,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "--input-jsonl", dest="input_path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input_path.exists():
        raise SystemExit(f"Input not found: {args.input_path}")

    records, load_errors, input_kind = load_records(args.input_path)
    report = check_records(records, load_errors, args.input_path, input_kind)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

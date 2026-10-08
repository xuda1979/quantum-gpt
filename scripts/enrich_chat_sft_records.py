#!/usr/bin/env python3
"""Enrich chat-SFT JSONL splits with task-structure fields used by research methods."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.task_metadata import resolve_test_path
from training.grpo_utils import (
    estimate_detail_budget,
    extract_behavior_hints_from_test_source,
    summarize_python_interface,
)

SINGLE_FILE_GUARDRAILS = [
    "Keep the answer self-contained in one Python file.",
    "Do not depend on repository-local helpers or invent non-standard modules.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--behavior-cap", type=int, default=6)
    parser.add_argument("--detail-budget-cap", type=int, default=8)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _task_dir_from_record(record: dict[str, Any]) -> Path:
    metadata = record.get("metadata") or {}
    task_dir_value = metadata.get("source_task_dir")
    if not task_dir_value:
        raise SystemExit(f"Missing metadata.source_task_dir for example {record.get('example_id')}")
    task_dir = Path(str(task_dir_value))
    if not task_dir.is_absolute():
        task_dir = ROOT / task_dir
    if not task_dir.exists():
        raise FileNotFoundError(
            f"Task directory not found for example {record.get('example_id')}: {task_dir}"
        )
    return task_dir


def _candidate_paths(task_dir: Path, task_meta: dict[str, Any]) -> list[Path]:
    candidate_files = task_meta.get("candidate_files")
    if candidate_files:
        return [task_dir / str(relative_path) for relative_path in candidate_files]
    candidate_file = task_meta.get("candidate_file")
    if candidate_file:
        return [task_dir / str(candidate_file)]
    return []


def _unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _user_prompt(record: dict[str, Any]) -> str:
    for message in record.get("messages") or []:
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


def _extract_bullets(section_text: str) -> list[str]:
    bullets: list[str] = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def _extract_prompt_section(prompt: str, heading: str) -> str:
    marker = f"{heading}:\n"
    if marker not in prompt:
        return ""
    tail = prompt.split(marker, 1)[1]
    blocks = tail.split("\n\n", 1)
    return blocks[0]


def _append_single_file_guardrails(prompt: str, *, task_meta: dict[str, Any]) -> str:
    if task_meta.get("candidate_files"):
        return prompt
    if "Single-file guardrails:\n" in prompt:
        return prompt
    if all(guardrail in prompt for guardrail in SINGLE_FILE_GUARDRAILS):
        return prompt
    guardrails = "\n".join(f"- {line}" for line in SINGLE_FILE_GUARDRAILS)
    return f"{prompt.rstrip()}\n\nSingle-file guardrails:\n{guardrails}\n"


def _fallback_fields_from_prompt(
    record: dict[str, Any], *, detail_budget_cap: int
) -> tuple[list[str], list[str], int]:
    prompt = _user_prompt(record)
    interface_lines = _extract_bullets(_extract_prompt_section(prompt, "Required interface"))
    behavior_hints = _extract_bullets(_extract_prompt_section(prompt, "Behavioral requirements"))
    if not behavior_hints:
        behavior_hints = _extract_bullets(_extract_prompt_section(prompt, "Implementation notes"))
    detail_budget = min(detail_budget_cap, max(1, len(interface_lines) + len(behavior_hints)))
    return interface_lines, behavior_hints, detail_budget


def enrich_record(
    record: dict[str, Any], *, behavior_cap: int, detail_budget_cap: int
) -> dict[str, Any]:
    enriched = copy.deepcopy(record)
    task_meta: dict[str, Any] = {}
    try:
        task_dir = _task_dir_from_record(enriched)
        task_meta = load_json(task_dir / "task.json")
        test_path = resolve_test_path(task_dir, task_meta)
        test_source = test_path.read_text(encoding="utf-8")

        interface_lines: list[str] = []
        for candidate_path in _candidate_paths(task_dir, task_meta):
            if not candidate_path.exists():
                continue
            interface_lines.extend(
                summarize_python_interface(candidate_path.read_text(encoding="utf-8"))
            )
        interface_lines = _unique_preserve_order(interface_lines)

        behavior_hints = extract_behavior_hints_from_test_source(test_source, cap=behavior_cap)
        detail_budget = max(
            estimate_detail_budget(test_source, cap=detail_budget_cap),
            min(detail_budget_cap, max(1, len(behavior_hints))) if behavior_hints else 1,
        )
        enrichment_source = "task_artifacts"
    except (FileNotFoundError, SystemExit):
        interface_lines, behavior_hints, detail_budget = _fallback_fields_from_prompt(
            enriched,
            detail_budget_cap=detail_budget_cap,
        )
        enrichment_source = "prompt_fallback"

    enriched["required_interface"] = interface_lines
    enriched["behavior_hints"] = behavior_hints
    enriched["detail_budget"] = detail_budget

    metadata = dict(enriched.get("metadata") or {})
    metadata["enrichment_source"] = enrichment_source
    metadata["required_interface_count"] = len(interface_lines)
    metadata["behavior_hint_count"] = len(behavior_hints)
    metadata["detail_budget"] = detail_budget
    enriched["metadata"] = metadata

    messages = list(enriched.get("messages") or [])
    for message in messages:
        if message.get("role") == "user":
            message["content"] = _append_single_file_guardrails(
                str(message.get("content", "")),
                task_meta=task_meta,
            )
            break
    enriched["messages"] = messages
    return enriched


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    interface_counter = Counter()
    hint_counter = Counter()
    detail_counter = Counter()
    for row in rows:
        interface_counter[str(len(row.get("required_interface") or []))] += 1
        hint_counter[str(len(row.get("behavior_hints") or []))] += 1
        detail_counter[str(int(row.get("detail_budget") or 0))] += 1
    return {
        "count": len(rows),
        "required_interface_count_histogram": dict(sorted(interface_counter.items())),
        "behavior_hint_count_histogram": dict(sorted(hint_counter.items())),
        "detail_budget_histogram": dict(
            sorted(detail_counter.items(), key=lambda item: int(item[0]))
        ),
    }


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    split_summaries: dict[str, Any] = {}
    for split_name in ("train", "eval"):
        input_path = args.input_dir / f"{split_name}.jsonl"
        if not input_path.exists():
            continue
        rows = load_jsonl(input_path)
        enriched_rows = [
            enrich_record(
                row, behavior_cap=args.behavior_cap, detail_budget_cap=args.detail_budget_cap
            )
            for row in rows
        ]
        write_jsonl(args.out_dir / f"{split_name}.jsonl", enriched_rows)
        split_summaries[split_name] = summarize_rows(enriched_rows)

    source_manifest_path = args.input_dir / "manifest.json"
    manifest: dict[str, Any] = {
        "manifest_version": "chat-sft-enriched-v1",
        "input_dir": str(args.input_dir),
        "out_dir": str(args.out_dir),
        "behavior_cap": args.behavior_cap,
        "detail_budget_cap": args.detail_budget_cap,
        "source_manifest": str(source_manifest_path) if source_manifest_path.exists() else None,
        "split_summaries": split_summaries,
    }
    if source_manifest_path.exists():
        manifest["source_manifest_payload"] = load_json(source_manifest_path)
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

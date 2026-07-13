#!/usr/bin/env python3
"""Build a diverse, high-quality quantum-coding Q&A dataset authored by Opus 4.8.

This module stores 100 hand-authored quantum software engineering question/answer
pairs (each answer includes runnable Python code and a quick check). It wraps each
pair into the local ``dataset-v0`` contract used by the ASI2 distillation pipeline
so the rows can flow straight into the existing filter/chatml/split tooling.

The content here is authored directly by the assistant (Claude Opus 4.8) acting as
the teacher, not fetched from an external API.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pkgutil
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "opus_quantum_qa_v1.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "generated" / "opus_quantum_qa_v1_manifest.json"
BATCH_PACKAGE = "tools.opus_qa_batches"

SCHEMA_VERSION = "dataset-v0"
SOURCE_NAME = "opus_4_8_quantum_qa_hard_sft"
TEACHER_MODEL = "Claude-Opus-4.8"
STUDENT_MODEL = "Qwen/Qwen3.6-35B-A3B"
TARGET_ENV = "ASI2"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "quantum_qa"


# Authored pairs live in Python batch modules under tools/opus_qa_batches/, each
# exposing a top-level list ``PAIRS``. Each pair is a dict with fields:
#   framework, task_type, category, difficulty, title, instruction, response
# task_type in: implementation, repair, optimization, unit_testing, noise_modeling,
#   hardware_mapping, error_mitigation, algorithm_implementation, agentic_trajectory,
#   verification_plan, api_grounded_qa, multi_framework_port


def load_pairs() -> list[dict[str, Any]]:
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    package = importlib.import_module(BATCH_PACKAGE)
    pairs: list[dict[str, Any]] = []
    module_names = sorted(m.name for m in pkgutil.iter_modules(package.__path__))
    for name in module_names:
        if not name.startswith("batch_"):
            continue
        module = importlib.import_module(f"{BATCH_PACKAGE}.{name}")
        batch = getattr(module, "PAIRS", None)
        if not isinstance(batch, list):
            raise ValueError(f"{name}: PAIRS must be a list")
        pairs.extend(batch)
    return pairs


def build_row(index: int, pair: dict[str, Any]) -> dict[str, Any]:
    required = {
        "framework",
        "task_type",
        "category",
        "difficulty",
        "title",
        "instruction",
        "response",
    }
    missing = required - set(pair)
    if missing:
        raise ValueError(f"pair {index} missing fields: {sorted(missing)}")
    title = pair["title"]
    slug = slugify(title)
    instruction = pair["instruction"].strip()
    response = pair["response"].strip()
    if "<think" in response.lower() or "<think" in instruction.lower():
        raise ValueError(f"pair {index} ({slug}) contains forbidden think tag")
    digest = hashlib.sha256(f"{title}\n{instruction}".encode()).hexdigest()
    framework = pair["framework"]
    tags = sorted(
        {
            "quantum",
            "distillation",
            "hard_sft",
            "opus_authored",
            pair["task_type"],
            pair["category"],
            *([framework] if framework else []),
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "example_id": f"opus_qa_{index:03d}_{slug}"[:120],
        "domain": "quantum",
        "category": pair["category"],
        "task_type": pair["task_type"],
        "source": SOURCE_NAME,
        "difficulty": pair["difficulty"],
        "language": "python",
        "framework": framework,
        "tags": tags,
        "instruction": instruction,
        "response": response,
        "artifacts": {
            "teacher_prompt_policy": "concise_rationale_summary_plus_final_answer",
            "verification_targets": [
                "python_syntax",
                "unit_tests_when_available",
                "quantum_simulator_smoke",
                "static_api_consistency",
            ],
            "content_sha256": digest,
        },
        "metadata": {
            "task_id": f"opus_qa_{slug}",
            "title": title,
            "student_model": STUDENT_MODEL,
            "teacher_model": TEACHER_MODEL,
            "target_env": TARGET_ENV,
            "distillation_strategy": "hard_sft_self_authored_teacher",
            "distillation_phase": "opus_self_authored_qa",
            "authored_by": "Claude-Opus-4.8",
        },
    }


def build_rows() -> list[dict[str, Any]]:
    pairs = load_pairs()
    rows = [build_row(i, pair) for i, pair in enumerate(pairs, start=1)]
    seen: set[str] = set()
    for row in rows:
        eid = row["example_id"]
        if eid in seen:
            raise ValueError(f"duplicate example_id: {eid}")
        seen.add(eid)
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "framework": dict(sorted(Counter(str(r["framework"]) for r in rows).items())),
        "task_type": dict(sorted(Counter(r["task_type"] for r in rows).items())),
        "category": dict(sorted(Counter(r["category"] for r in rows).items())),
        "difficulty": dict(sorted(Counter(r["difficulty"] for r in rows).items())),
        "teacher_model": TEACHER_MODEL,
        "student_model": STUDENT_MODEL,
        "target_env": TARGET_ENV,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--min-count", type=int, default=100)
    args = parser.parse_args()

    rows = build_rows()
    if len(rows) < args.min_count:
        raise SystemExit(f"expected at least {args.min_count} pairs, got {len(rows)}")
    write_jsonl(args.output, rows)
    summary = summarize(rows)
    manifest = {
        "manifest_version": "opus-quantum-qa-v1",
        "format": SCHEMA_VERSION,
        "output": str(args.output),
        "summary": summary,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

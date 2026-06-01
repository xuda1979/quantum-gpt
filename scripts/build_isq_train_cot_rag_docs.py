#!/usr/bin/env python3
"""Convert ISQ training QA/COT JSON into Markdown documents for RAG indexing."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "generated" / "isq_train_cot_rag"


def _slug(value: object, *, fallback: str = "uncategorized") -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = text.strip("-._")
    return text or fallback


def _clean_text(value: object) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return re.sub(r"\n{3,}", "\n\n", text)


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def render_record(record: dict[str, Any], *, ordinal: int) -> str:
    task_id = _clean_text(record.get("task_id")) or f"isq-record-{ordinal}"
    task_type = _clean_text(record.get("task_type"))
    category = _clean_text(record.get("category"))
    difficulty = _clean_text(record.get("difficulty"))
    source = _clean_text(record.get("source"))
    dataset_index = _clean_text(record.get("dataset_index"))
    tags = _as_list(record.get("concept_tags"))
    prompt = _clean_text(record.get("prompt"))
    reasoning = _clean_text(record.get("cot_reasoning"))
    answer = _clean_text(record.get("reference_answer"))

    parts = [
        f"## {task_id}",
        "",
        f"- task_id: `{task_id}`",
    ]
    if task_type:
        parts.append(f"- task_type: `{task_type}`")
    if category:
        parts.append(f"- category: `{category}`")
    if difficulty:
        parts.append(f"- difficulty: `{difficulty}`")
    if tags:
        parts.append("- concept_tags: " + ", ".join(f"`{tag}`" for tag in tags))
    if source:
        parts.append(f"- source: `{source}`")
    if dataset_index:
        parts.append(f"- dataset_index: `{dataset_index}`")
    parts.extend(["", "### Prompt", "", prompt or "(empty prompt)"])
    if reasoning:
        parts.extend(["", "### Chain-of-thought reasoning", "", reasoning])
    if answer:
        parts.extend(["", "### Reference answer", "", answer])
    return "\n".join(parts).strip() + "\n"


def load_records(source: Path) -> list[dict[str, Any]]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("ISQ training data must be a JSON list")
    records: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"record {index} is not an object")
        records.append(item)
    return records


def write_docs(
    records: list[dict[str, Any]],
    output_dir: Path,
    *,
    records_per_file: int,
    clean: bool,
) -> dict[str, Any]:
    if records_per_file <= 0:
        raise ValueError("records_per_file must be > 0")
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_category: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for ordinal, record in enumerate(records, start=1):
        by_category[_slug(record.get("category"))].append((ordinal, record))

    written_files: list[str] = []
    category_counts: Counter[str] = Counter()
    for category in sorted(by_category):
        items = by_category[category]
        category_counts[category] = len(items)
        for shard_index, start in enumerate(range(0, len(items), records_per_file), start=1):
            shard = items[start : start + records_per_file]
            path = output_dir / f"{category}-{shard_index:03d}.md"
            body = [
                f"# ISQ training COT RAG corpus: {category} shard {shard_index}",
                "",
                "This generated document converts user-provided ISQ training examples into",
                "retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.",
                "",
            ]
            body.extend(render_record(record, ordinal=ordinal) for ordinal, record in shard)
            path.write_text("\n".join(body).strip() + "\n", encoding="utf-8")
            written_files.append(path.relative_to(output_dir).as_posix())

    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# ISQ Training COT RAG Corpus",
                "",
                "Generated from the user-provided `isq_train_cot.json` file.",
                "Each Markdown shard contains prompts, metadata, optional COT reasoning,",
                "and reference answers for ISQ and quantum-code retrieval grounding.",
                "",
                "Regenerate with:",
                "",
                "```bash",
                "python scripts/build_isq_train_cot_rag_docs.py --source /path/to/isq_train_cot.json",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    written_files.insert(0, "README.md")

    manifest = {
        "record_count": len(records),
        "category_count": len(category_counts),
        "categories": dict(sorted(category_counts.items())),
        "records_per_file": records_per_file,
        "file_count": len(written_files),
        "files": written_files,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--records-per-file", type=int, default=10)
    parser.add_argument("--no-clean", action="store_true", help="Do not remove existing generated docs first.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_records(args.source)
    manifest = write_docs(
        records,
        args.output_dir,
        records_per_file=args.records_per_file,
        clean=not args.no_clean,
    )
    print(json.dumps({"output_dir": str(args.output_dir), **manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

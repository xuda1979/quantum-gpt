#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.prepare_pdf_dataset import prepare_datasets


TEXT_SUFFIXES = {".txt", ".md", ".tex"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Paper roots or files (.pdf/.txt/.md/.tex)")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", default="paper_sft")
    parser.add_argument("--train-ratio", type=float, default=0.9)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--chunk-size", type=int, default=2400)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--min-chunk-length", type=int, default=400)
    return parser.parse_args()


def iter_text_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path
            continue
        if not path.is_dir():
            continue
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() in TEXT_SUFFIXES:
                yield candidate


def build_messages_from_record(record: dict) -> dict:
    assistant_parts = []
    analysis = record.get("analysis")
    if analysis:
        assistant_parts.append(f"Analysis:\n{analysis}")
    assistant_parts.append(f"Answer:\n{record['code']}")
    return {
        "example_id": f"paper::{record['metadata']['source']}::{record['metadata']['chunk_index']}",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a quantum-computing research assistant. Preserve mathematically and "
                    "implementation-relevant details when summarizing paper excerpts."
                ),
            },
            {"role": "user", "content": record["prompt"]},
            {"role": "assistant", "content": "\n\n".join(assistant_parts)},
        ],
        "metadata": record["metadata"],
    }


def chunk_text_document(text: str, *, chunk_size: int, chunk_overlap: int) -> list[tuple[str, int, int]]:
    from tools.pdf_to_sft import _clean_page_text, _strip_reference_section, chunk_text

    cleaned = _clean_page_text(text)
    stripped = _strip_reference_section(cleaned)
    return chunk_text(stripped, chunk_size, chunk_overlap)


def prepare_text_documents(paths: list[Path], output_dir: Path, dataset_name: str, *, chunk_size: int, chunk_overlap: int, min_chunk_length: int, train_ratio: float, seed: int) -> tuple[Path, Path | None]:
    records: list[dict] = []
    for path in iter_text_files(paths):
        body = path.read_text(encoding="utf-8", errors="ignore")
        for index, (chunk, start, end) in enumerate(
            chunk_text_document(body, chunk_size=chunk_size, chunk_overlap=chunk_overlap),
            start=1,
        ):
            if len(chunk.strip()) < min_chunk_length:
                continue
            records.append(
                {
                    "prompt": (
                        "Read the following quantum-computing paper excerpt and produce a concise technical summary "
                        "that preserves the main algorithmic, mathematical, and implementation-relevant details.\n\n"
                        f"{chunk}"
                    ),
                    "code": chunk,
                    "analysis": (
                        f"Identify the main claim, the key quantum or coding concepts, and any implementation "
                        f"constraints for chunk {index}."
                    ),
                    "metadata": {
                        "source": str(path),
                        "chunk_index": index,
                        "char_start": start,
                        "char_end": end,
                    },
                }
            )

    import random

    random.Random(seed).shuffle(records)
    all_messages = [build_messages_from_record(record) for record in records]
    split_index = int(len(all_messages) * train_ratio)
    train_messages = all_messages[:split_index]
    valid_messages = all_messages[split_index:]

    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / f"{dataset_name}_messages_train.jsonl"
    with train_path.open("w", encoding="utf-8") as handle:
        for row in train_messages:
            json.dump(row, handle, ensure_ascii=False)
            handle.write("\n")

    valid_path: Path | None = None
    if valid_messages:
        valid_path = output_dir / f"{dataset_name}_messages_valid.jsonl"
        with valid_path.open("w", encoding="utf-8") as handle:
            for row in valid_messages:
                json.dump(row, handle, ensure_ascii=False)
                handle.write("\n")
    return train_path, valid_path


def main() -> int:
    args = parse_args()
    paths = [Path(item) for item in args.inputs]
    pdf_roots = [path for path in paths if path.is_dir() or path.suffix.lower() == ".pdf"]
    text_roots = [path for path in paths if path.is_dir() or path.suffix.lower() in TEXT_SUFFIXES]

    pdf_train_path, pdf_valid_path = prepare_datasets(
        pdf_roots,
        args.output_dir / "pdf_records",
        dataset_name=args.dataset_name,
        train_ratio=args.train_ratio,
        seed=args.seed,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_length=args.min_chunk_length,
    )

    text_train_path, text_valid_path = prepare_text_documents(
        text_roots,
        args.output_dir / "messages",
        args.dataset_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_length=args.min_chunk_length,
        train_ratio=args.train_ratio,
        seed=args.seed,
    )

    result = {
        "status": "ok",
        "pdf_records_train": str(pdf_train_path),
        "pdf_records_valid": str(pdf_valid_path) if pdf_valid_path else None,
        "messages_train": str(text_train_path),
        "messages_valid": str(text_valid_path) if text_valid_path else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

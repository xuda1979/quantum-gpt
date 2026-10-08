from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

from tools import pdf_to_sft


DEFAULT_INSTRUCTION_TEMPLATE = (
    "Read the following quantum-computing paper excerpt and produce a concise technical summary "
    "that preserves the main algorithmic, mathematical, and implementation-relevant details.\n\n{chunk}"
)
DEFAULT_TARGET_TEMPLATE = "{chunk}"
DEFAULT_ANALYSIS_TEMPLATE = (
    "Identify the main claim, the key quantum or coding concepts, and any implementation constraints for chunk {index}."
)


def _collect_records(
    pdf_roots: Iterable[Path],
    *,
    chunk_size: int = 2400,
    chunk_overlap: int = 200,
    instruction_template: str = DEFAULT_INSTRUCTION_TEMPLATE,
    target_template: str = DEFAULT_TARGET_TEMPLATE,
    analysis_template: str | None = DEFAULT_ANALYSIS_TEMPLATE,
    min_chunk_length: int = 400,
    strip_references: bool = True,
) -> list[dict]:
    pdf_paths = list(pdf_to_sft.iter_pdf_files(pdf_roots))
    return list(
        pdf_to_sft.build_records(
            pdf_paths=pdf_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            instruction_template=instruction_template,
            target_template=target_template,
            analysis_template=analysis_template,
            min_chunk_length=min_chunk_length,
            strip_references=strip_references,
        )
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            json.dump(row, handle, ensure_ascii=False)
            handle.write("\n")


def prepare_datasets(
    pdf_root: Path | Iterable[Path],
    output_dir: Path,
    *,
    dataset_name: str,
    train_ratio: float = 0.9,
    seed: int = 42,
    chunk_size: int = 2400,
    chunk_overlap: int = 200,
    instruction_template: str = DEFAULT_INSTRUCTION_TEMPLATE,
    target_template: str = DEFAULT_TARGET_TEMPLATE,
    analysis_template: str | None = DEFAULT_ANALYSIS_TEMPLATE,
    min_chunk_length: int = 400,
    strip_references: bool = True,
) -> tuple[Path, Path | None]:
    roots = [pdf_root] if isinstance(pdf_root, Path) else list(pdf_root)
    records = _collect_records(
        roots,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        instruction_template=instruction_template,
        target_template=target_template,
        analysis_template=analysis_template,
        min_chunk_length=min_chunk_length,
        strip_references=strip_references,
    )
    random.Random(seed).shuffle(records)

    output_dir.mkdir(parents=True, exist_ok=True)
    all_path = output_dir / f"{dataset_name}_all.jsonl"
    _write_jsonl(all_path, records)

    split_index = int(len(records) * train_ratio)
    train_records = records[:split_index]
    valid_records = records[split_index:]

    train_path = output_dir / f"{dataset_name}_train.jsonl"
    _write_jsonl(train_path, train_records)

    valid_path: Path | None = None
    if valid_records:
        valid_path = output_dir / f"{dataset_name}_valid.jsonl"
        _write_jsonl(valid_path, valid_records)

    return train_path, valid_path


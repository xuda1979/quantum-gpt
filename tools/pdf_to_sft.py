from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator


REFERENCE_HEADING_RE = re.compile(r"(?im)^\s*(references|bibliography)\s*$")


def iter_pdf_files(roots: Iterable[Path]) -> Iterator[Path]:
    for root in roots:
        path = Path(root)
        if path.is_file() and path.suffix.lower() == ".pdf":
            yield path
            continue
        if not path.is_dir():
            continue
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() == ".pdf":
                yield candidate


def extract_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - exercised only when dependency is absent
        raise SystemExit(
            "pypdf is required for PDF extraction. Install it before preparing paper datasets."
        ) from exc

    reader = PdfReader(str(path))
    page_texts = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")
    return "\n\n".join(page_texts)


def _clean_page_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"-\n\s*", "", normalized)
    lines = []
    for raw_line in normalized.split("\n"):
        stripped = " ".join(raw_line.split())
        lines.append(stripped)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _strip_reference_section(body: str) -> str:
    for match in REFERENCE_HEADING_RE.finditer(body):
        prefix = body[: match.start()].strip()
        if prefix:
            return prefix
    return body


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[tuple[str, int, int]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[tuple[str, int, int]] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append((chunk, start, end))
        if end >= len(text):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def _process_single_pdf(
    pdf_path: Path,
    *,
    chunk_size: int,
    chunk_overlap: int,
    instruction_template: str,
    target_template: str,
    analysis_template: str | None,
    min_chunk_length: int,
    strip_references: bool,
) -> list[dict]:
    text = _clean_page_text(extract_text_from_pdf(pdf_path))
    if strip_references:
        text = _strip_reference_section(text)

    records = []
    for index, (chunk, start, end) in enumerate(chunk_text(text, chunk_size, chunk_overlap), start=1):
        if len(chunk.strip()) < min_chunk_length:
            continue
        format_args = {
            "index": index,
            "chunk": chunk,
            "source": str(pdf_path),
            "start": start,
            "end": end,
        }
        record = {
            "prompt": instruction_template.format(**format_args),
            "code": target_template.format(**format_args),
            "metadata": {
                "source": str(pdf_path),
                "chunk_index": index,
                "char_start": start,
                "char_end": end,
            },
        }
        if analysis_template is not None:
            record["analysis"] = analysis_template.format(**format_args)
        records.append(record)
    return records


def build_records(
    *,
    pdf_paths: Iterable[Path],
    chunk_size: int,
    chunk_overlap: int,
    instruction_template: str,
    target_template: str,
    analysis_template: str | None,
    min_chunk_length: int,
    strip_references: bool,
) -> Iterator[dict]:
    for pdf_path in pdf_paths:
        yield from _process_single_pdf(
            Path(pdf_path),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            instruction_template=instruction_template,
            target_template=target_template,
            analysis_template=analysis_template,
            min_chunk_length=min_chunk_length,
            strip_references=strip_references,
        )


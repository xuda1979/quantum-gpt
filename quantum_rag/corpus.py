from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator


DEFAULT_ALLOWED_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".jsonl",
    ".ipynb",
    ".tex",
    ".yaml",
    ".yml",
}

DEFAULT_EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "models",
    "outputs",
    ".local-python",
}

DEFAULT_EXCLUDED_PATH_PARTS = {
    "artifacts/runtime-bundles",
    "artifacts/ai2_code_docs_snapshot",
}

PDF_EXTENSIONS = {".pdf"}


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_path: str
    title: str
    text: str
    char_start: int
    char_end: int
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _is_excluded_path(path: Path) -> bool:
    if any(part in DEFAULT_EXCLUDED_DIR_NAMES for part in path.parts):
        return True
    path_str = path.as_posix()
    return any(excluded in path_str for excluded in DEFAULT_EXCLUDED_PATH_PARTS)


def iter_source_files(
    roots: Iterable[Path],
    *,
    allowed_extensions: set[str] | None = None,
) -> Iterator[Path]:
    allowed = allowed_extensions or (DEFAULT_ALLOWED_EXTENSIONS | PDF_EXTENSIONS)
    for root in roots:
        candidate = Path(root)
        if not candidate.exists():
            continue
        if candidate.is_file():
            if candidate.suffix.lower() in allowed and not _is_excluded_path(candidate):
                if candidate.suffix.lower() in PDF_EXTENSIONS and not _pdf_support_available():
                    continue
                yield candidate
            continue
        for path in sorted(candidate.rglob("*")):
            if not path.is_file():
                continue
            if _is_excluded_path(path):
                continue
            if path.suffix.lower() in allowed:
                if path.suffix.lower() in PDF_EXTENSIONS and not _pdf_support_available():
                    continue
                yield path


def _pdf_support_available() -> bool:
    try:
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


def _load_ipynb_text(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cells = payload.get("cells", [])
    parts: list[str] = []
    for index, cell in enumerate(cells, start=1):
        cell_type = str(cell.get("cell_type", "unknown")).strip()
        source = cell.get("source", [])
        if isinstance(source, list):
            body = "".join(str(line) for line in source)
        else:
            body = str(source)
        body = body.strip()
        if not body:
            continue
        parts.append(f"[{cell_type} cell {index}]\n{body}")
    return "\n\n".join(parts)


def _load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depends on optional local install
        raise RuntimeError(
            "PDF ingestion requires `pypdf`. Install it locally before indexing PDF sources."
        ) from exc

    reader = PdfReader(str(path))
    return "\n\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()


def load_source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".ipynb":
        return _load_ipynb_text(path)
    if suffix == ".pdf":
        return _load_pdf_text(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def _normalize_path_for_preamble(path: Path) -> str:
    """Turn a source path into a human-readable preamble line for indexing.

    The preamble makes directory names, file stems, and task identifiers
    visible to BM25 and TF-IDF so that queries like "QFT phase pattern task"
    can match on the path component ``qft_phase_pattern`` even when the chunk
    body does not contain the phrase verbatim.
    """
    parts = path.parts
    # Use at most the last 4 path components to keep preamble compact
    suffix_parts = parts[-4:] if len(parts) > 4 else parts
    readable = "/".join(suffix_parts)
    # Also expand underscores so "qft_phase_pattern" becomes searchable as
    # "qft phase pattern" in addition to the joined form.
    expanded = readable.replace("_", " ")
    return f"[source: {readable}] [{expanded}]"


def _extract_task_metadata(path: Path, text: str) -> str:
    """If *path* points to a task.json file, extract the task id/name as a
    preamble so that BM25/TF-IDF can match on structured task identifiers."""
    if path.name.lower() != "task.json":
        return ""
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return ""
    parts: list[str] = []
    task_id = payload.get("id")
    if isinstance(task_id, str) and task_id.strip():
        parts.append(f"task_id={task_id}")
        parts.append(task_id.replace("_", " "))
    task_name = payload.get("name")
    if isinstance(task_name, str) and task_name.strip():
        parts.append(f"task_name={task_name}")
    task_domain = payload.get("domain")
    if isinstance(task_domain, str) and task_domain.strip():
        parts.append(f"domain={task_domain}")
    task_category = payload.get("category")
    if isinstance(task_category, str) and task_category.strip():
        parts.append(f"category={task_category}")
    if parts:
        return "[task metadata: " + " | ".join(parts) + "]"
    return ""


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("\t", "    ")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _find_split_boundary(text: str, start: int, rough_end: int) -> int:
    if rough_end >= len(text):
        return len(text)

    window_start = max(start + 1, rough_end - 200)
    window_end = min(len(text), rough_end + 200)
    boundary_markers = ("\n\n", "\n", " ")
    best_end = rough_end
    best_score = float("inf")
    for marker in boundary_markers:
        candidate = text.rfind(marker, window_start, window_end)
        if candidate <= start:
            continue
        boundary = candidate + len(marker)
        score = abs(boundary - rough_end)
        if score < best_score:
            best_end = boundary
            best_score = score
    return max(start + 1, best_end)


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[tuple[str, int, int]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = _normalize_text(text)
    if not text:
        return []

    chunks: list[tuple[str, int, int]] = []
    start = 0
    while start < len(text):
        rough_end = min(len(text), start + chunk_size)
        end = _find_split_boundary(text, start, rough_end)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append((chunk, start, end))
        if end >= len(text):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def _make_chunk_id(path: Path, start: int, end: int) -> str:
    digest = hashlib.sha1(f"{path.as_posix()}:{start}:{end}".encode("utf-8")).hexdigest()
    return digest[:16]


def build_chunks_for_file(
    path: Path,
    *,
    chunk_size: int,
    chunk_overlap: int,
    min_chunk_chars: int,
    inject_path_preamble: bool = True,
) -> list[DocumentChunk]:
    raw_text = load_source_text(path)
    # Build preamble components that make path/metadata visible to BM25/TF-IDF
    preamble_parts: list[str] = []
    if inject_path_preamble:
        preamble_parts.append(_normalize_path_for_preamble(path))
        task_meta = _extract_task_metadata(path, raw_text)
        if task_meta:
            preamble_parts.append(task_meta)
    preamble = "\n".join(preamble_parts)

    chunks: list[DocumentChunk] = []
    for index, (chunk_text_value, start, end) in enumerate(
        chunk_text(raw_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap),
        start=1,
    ):
        if len(chunk_text_value) < min_chunk_chars:
            continue
        # Prepend preamble so every chunk carries source-path context
        augmented_text = f"{preamble}\n\n{chunk_text_value}" if preamble else chunk_text_value
        chunks.append(
            DocumentChunk(
                chunk_id=_make_chunk_id(path, start, end),
                source_path=path.as_posix(),
                title=path.name,
                text=augmented_text,
                char_start=start,
                char_end=end,
                metadata={
                    "chunk_index": index,
                    "extension": path.suffix.lower(),
                    "has_path_preamble": inject_path_preamble,
                },
            )
        )
    return chunks


def build_chunks_from_roots(
    roots: Iterable[Path],
    *,
    chunk_size: int = 1400,
    chunk_overlap: int = 200,
    min_chunk_chars: int = 250,
    allowed_extensions: set[str] | None = None,
    max_files: int | None = None,
    inject_path_preamble: bool = True,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for file_index, path in enumerate(
        iter_source_files(roots, allowed_extensions=allowed_extensions),
        start=1,
    ):
        if max_files is not None and file_index > max_files:
            break
        chunks.extend(
            build_chunks_for_file(
                path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                min_chunk_chars=min_chunk_chars,
                inject_path_preamble=inject_path_preamble,
            )
        )
    return chunks

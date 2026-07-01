#!/usr/bin/env python3
"""Check whether quantum eval tasks have authoritative RAG grounding.

This is a task-authoring gate for the integrated plan's RAG workstream.  It
does not ask a model to answer the task.  Instead it verifies that each quantum
task can retrieve at least one relevant source from the curated quantum docs
corpus before that task is promoted into datasets, benchmarks, or training.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag import QuantumRAGIndex, QueryExpansionConfig, build_chunks_from_roots, retrieve


DEFAULT_TASK_ROOT = ROOT / "evals" / "tasks" / "quantum"
DEFAULT_DOC_ROOT = ROOT / "docs" / "quantum_libraries"
DEFAULT_OUTPUT = ROOT / "reports" / "quantum_task_rag_grounding.json"

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+-]*")
STOPWORDS = {
    "and",
    "api",
    "classical",
    "code",
    "coding",
    "construction",
    "decoder",
    "function",
    "implementation",
    "lookup",
    "normalization",
    "python",
    "quantum",
    "repair",
    "simulation",
    "task",
    "tests",
}


@dataclass(frozen=True)
class TaskDescriptor:
    task_id: str
    name: str
    category: str
    task_path: str


@dataclass(frozen=True)
class SourceHit:
    rank: int
    source_path: str
    final_score: float
    lexical_score: float
    semantic_score: float
    matched_terms: list[str]
    preview: str


@dataclass(frozen=True)
class TaskGroundingResult:
    task_id: str
    name: str
    category: str
    task_path: str
    query: str
    grounded: bool
    best_score: float
    matched_terms: list[str]
    hits: list[SourceHit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--doc-root", action="append", type=Path, dest="doc_roots", default=[])
    parser.add_argument("--index", type=Path, default=None, help="Use an existing quantum RAG index.")
    parser.add_argument("--save-index", type=Path, default=None, help="Persist the built docs index.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--min-score", type=float, default=0.35)
    parser.add_argument("--min-matched-terms", type=int, default=1)
    parser.add_argument("--max-chunks-per-source", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=1400)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--min-chunk-chars", type=int, default=120)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-missing", action="store_true")
    return parser.parse_args()


def _tokenize(value: str) -> list[str]:
    terms: list[str] = []
    for raw in TOKEN_RE.findall(value.replace("_", " ")):
        token = raw.lower().strip("-+_")
        if len(token) < 3 or token in STOPWORDS:
            continue
        terms.append(token)
    return list(dict.fromkeys(terms))


def load_tasks(task_root: Path) -> list[TaskDescriptor]:
    tasks: list[TaskDescriptor] = []
    for task_json in sorted(task_root.glob("*/task.json")):
        payload = json.loads(task_json.read_text(encoding="utf-8"))
        task_id = str(payload.get("id", "")).strip()
        name = str(payload.get("name", "")).strip()
        category = str(payload.get("category", "")).strip()
        domain = str(payload.get("domain", "")).strip()
        if not task_id or domain != "quantum":
            continue
        tasks.append(
            TaskDescriptor(
                task_id=task_id,
                name=name,
                category=category,
                task_path=task_json.as_posix(),
            )
        )
    return tasks


def build_task_query(task: TaskDescriptor) -> str:
    query_parts = [
        task.task_id.replace("_", " "),
        task.name,
        task.category.replace("_", " "),
    ]
    return " ".join(part for part in query_parts if part).strip()


def expected_terms(task: TaskDescriptor) -> list[str]:
    return _tokenize(f"{task.task_id} {task.name} {task.category}")


def matched_terms_for_source(terms: Iterable[str], *, source_path: str, text: str) -> list[str]:
    haystack = f"{source_path}\n{text}".lower().replace("_", " ")
    return [term for term in terms if term in haystack]


def build_index(
    doc_roots: list[Path],
    *,
    chunk_size: int,
    chunk_overlap: int,
    min_chunk_chars: int,
) -> QuantumRAGIndex:
    chunks = build_chunks_from_roots(
        doc_roots,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        min_chunk_chars=min_chunk_chars,
    )
    if not chunks:
        raise ValueError("No RAG chunks were built from the provided doc roots")
    return QuantumRAGIndex.build(chunks)


def check_task_grounding(
    task: TaskDescriptor,
    *,
    index: QuantumRAGIndex,
    top_k: int,
    alpha: float,
    min_score: float,
    min_matched_terms: int,
    max_chunks_per_source: int | None,
) -> TaskGroundingResult:
    query = build_task_query(task)
    terms = expected_terms(task)
    retrieved = retrieve(
        index,
        query,
        top_k=top_k,
        alpha=alpha,
        expansion=QueryExpansionConfig(enabled=True),
        max_chunks_per_source=max_chunks_per_source,
    )

    hits: list[SourceHit] = []
    for item in retrieved:
        matched = matched_terms_for_source(
            terms,
            source_path=item.chunk.source_path,
            text=item.chunk.text,
        )
        hits.append(
            SourceHit(
                rank=item.rank,
                source_path=item.chunk.source_path,
                final_score=item.final_score,
                lexical_score=item.lexical_score,
                semantic_score=item.semantic_score,
                matched_terms=matched,
                preview=item.chunk.text[:240],
            )
        )

    qualifying_hits = [
        hit
        for hit in hits
        if hit.final_score >= min_score and len(hit.matched_terms) >= min_matched_terms
    ]
    best_score = max((hit.final_score for hit in hits), default=0.0)
    all_matched_terms = sorted({term for hit in hits for term in hit.matched_terms})
    return TaskGroundingResult(
        task_id=task.task_id,
        name=task.name,
        category=task.category,
        task_path=task.task_path,
        query=query,
        grounded=bool(qualifying_hits),
        best_score=best_score,
        matched_terms=all_matched_terms,
        hits=hits,
    )


def build_report(
    results: list[TaskGroundingResult],
    *,
    task_root: Path,
    doc_roots: list[Path],
    top_k: int,
    alpha: float,
    min_score: float,
    min_matched_terms: int,
    index_summary: dict[str, object],
) -> dict[str, object]:
    total = len(results)
    grounded_count = sum(item.grounded for item in results)
    missing = [item.task_id for item in results if not item.grounded]
    return {
        "ok": grounded_count == total,
        "task_root": task_root.as_posix(),
        "doc_roots": [root.as_posix() for root in doc_roots],
        "top_k": top_k,
        "alpha": alpha,
        "min_score": min_score,
        "min_matched_terms": min_matched_terms,
        "index": index_summary,
        "metrics": {
            "total_tasks": total,
            "grounded_tasks": grounded_count,
            "missing_tasks": len(missing),
            "grounded_rate": grounded_count / max(total, 1),
        },
        "missing_task_ids": missing,
        "tasks": [asdict(item) for item in results],
    }


def main() -> int:
    args = parse_args()
    task_root = args.task_root.resolve()
    doc_roots = [path.resolve() for path in (args.doc_roots or [DEFAULT_DOC_ROOT])]

    if args.index is not None:
        index = QuantumRAGIndex.load(args.index)
    else:
        index = build_index(
            doc_roots,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            min_chunk_chars=args.min_chunk_chars,
        )
        if args.save_index is not None:
            index.save(args.save_index)

    tasks = load_tasks(task_root)
    if not tasks:
        raise SystemExit(f"No quantum tasks found under {task_root}")

    results = [
        check_task_grounding(
            task,
            index=index,
            top_k=args.top_k,
            alpha=args.alpha,
            min_score=args.min_score,
            min_matched_terms=args.min_matched_terms,
            max_chunks_per_source=args.max_chunks_per_source,
        )
        for task in tasks
    ]
    report = build_report(
        results,
        task_root=task_root,
        doc_roots=doc_roots,
        top_k=args.top_k,
        alpha=args.alpha,
        min_score=args.min_score,
        min_matched_terms=args.min_matched_terms,
        index_summary=index.summary(),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        metrics = report["metrics"]
        print(f"Quantum task RAG grounding: {metrics['grounded_tasks']}/{metrics['total_tasks']}")
        print(f"Grounded rate: {metrics['grounded_rate']:.3f}")
        print(f"Report: {args.output}")
        for item in results:
            status = "OK" if item.grounded else "MISSING"
            top_source = item.hits[0].source_path if item.hits else "<none>"
            print(f"[{status}] {item.task_id} best={item.best_score:.3f} top={top_source}")

    return 1 if args.fail_on_missing and not report["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

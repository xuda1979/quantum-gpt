#!/usr/bin/env python3
"""Score the repo-local quantum RAG retriever on a small benchmark set."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag.index import QuantumRAGIndex
from quantum_rag.retrieval import QueryExpansionConfig, retrieve


@dataclass(frozen=True)
class RetrievalExampleResult:
    id: str
    query: str
    expected_source_substrings: list[str]
    top_k: int
    hit_at_k: bool
    reciprocal_rank: float
    first_hit_rank: int | None
    retrieved_sources: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "test-index.pkl.gz",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=ROOT / "evals" / "benchmarks" / "quantum_rag_retrieval_v1.json",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--disable-query-expansion", action="store_true")
    parser.add_argument("--max-chunks-per-source", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def _load_benchmark(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Benchmark file must contain a JSON list")
    return payload


def _matches_expected(source: str, expected_source_substrings: list[str]) -> bool:
    return any(item in source for item in expected_source_substrings)


def score_example(
    benchmark_item: dict[str, object],
    *,
    index: QuantumRAGIndex,
    top_k: int,
    alpha: float,
    query_expansion_enabled: bool,
    max_chunks_per_source: int | None,
    exclude_source_substrings: list[str],
) -> RetrievalExampleResult:
    query = str(benchmark_item["query"])
    expected = [str(item) for item in benchmark_item["expected_source_substrings"]]
    results = retrieve(
        index,
        query,
        top_k=top_k,
        alpha=alpha,
        expansion=QueryExpansionConfig(enabled=query_expansion_enabled),
        max_chunks_per_source=max_chunks_per_source,
        exclude_source_substrings=exclude_source_substrings,
    )
    retrieved_sources = [item.chunk.source_path for item in results]

    first_hit_rank: int | None = None
    for item in results:
        if _matches_expected(item.chunk.source_path, expected):
            first_hit_rank = item.rank
            break

    reciprocal_rank = 0.0 if first_hit_rank is None else 1.0 / first_hit_rank
    return RetrievalExampleResult(
        id=str(benchmark_item["id"]),
        query=query,
        expected_source_substrings=expected,
        top_k=top_k,
        hit_at_k=first_hit_rank is not None,
        reciprocal_rank=reciprocal_rank,
        first_hit_rank=first_hit_rank,
        retrieved_sources=retrieved_sources,
    )


def build_report(
    example_results: list[RetrievalExampleResult],
    *,
    top_k: int,
    benchmark_path: Path,
    index_path: Path,
    alpha: float,
    query_expansion_enabled: bool,
    max_chunks_per_source: int | None,
    exclude_source_substrings: list[str],
) -> dict[str, object]:
    total = len(example_results)
    hit_count = sum(item.hit_at_k for item in example_results)
    mean_rr = sum(item.reciprocal_rank for item in example_results) / max(total, 1)
    return {
        "benchmark": str(benchmark_path),
        "index": str(index_path),
        "top_k": top_k,
        "alpha": alpha,
        "query_expansion_enabled": query_expansion_enabled,
        "max_chunks_per_source": max_chunks_per_source,
        "excluded_source_substrings": exclude_source_substrings,
        "metrics": {
            f"hit@{top_k}": hit_count / max(total, 1),
            "mrr": mean_rr,
            "total_examples": total,
            "hit_count": hit_count,
        },
        "examples": [asdict(item) for item in example_results],
    }


def main() -> int:
    args = parse_args()
    index = QuantumRAGIndex.load(args.index)
    benchmark = _load_benchmark(args.benchmark)
    query_expansion_enabled = not args.disable_query_expansion
    exclude_source_substrings = [
        args.benchmark.as_posix(),
        "reports/quantum_rag_retrieval_",
    ]
    example_results = [
        score_example(
            item,
            index=index,
            top_k=args.top_k,
            alpha=args.alpha,
            query_expansion_enabled=query_expansion_enabled,
            max_chunks_per_source=args.max_chunks_per_source,
            exclude_source_substrings=exclude_source_substrings,
        )
        for item in benchmark
    ]
    report = build_report(
        example_results,
        top_k=args.top_k,
        benchmark_path=args.benchmark,
        index_path=args.index,
        alpha=args.alpha,
        query_expansion_enabled=query_expansion_enabled,
        max_chunks_per_source=args.max_chunks_per_source,
        exclude_source_substrings=exclude_source_substrings,
    )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        metrics = report["metrics"]
        print(f"Benchmark: {args.benchmark}")
        print(f"Index: {args.index}")
        print(f"hit@{args.top_k}: {metrics[f'hit@{args.top_k}']:.3f}")
        print(f"MRR: {metrics['mrr']:.3f}")
        print(f"Hits: {metrics['hit_count']}/{metrics['total_examples']}")
        for item in example_results:
            status = "HIT" if item.hit_at_k else "MISS"
            print(f"[{status}] {item.id} rr={item.reciprocal_rank:.3f} first_hit_rank={item.first_hit_rank}")
            for source in item.retrieved_sources:
                print(f"    {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

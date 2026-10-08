#!/usr/bin/env python3
"""Run the retrieval benchmark against a quantum RAG index and report metrics.

Usage:

    # Default: authoritative index, quantum_rag_retrieval_v1.json benchmark
    python3 scripts/eval_quantum_rag.py

    # Specify a different index or benchmark
    python3 scripts/eval_quantum_rag.py \
        --index artifacts/quantum-rag/default-index.pkl.gz \
        --benchmark evals/benchmarks/quantum_rag_retrieval_v1.json

    # Output JSON report to a file
    python3 scripts/eval_quantum_rag.py --json --output reports/rag_eval_latest.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag.index import QuantumRAGIndex
from quantum_rag.retrieval import retrieve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "authoritative-index.pkl.gz",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=ROOT / "evals" / "benchmarks" / "quantum_rag_retrieval_v1.json",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    parser.add_argument("--output", type=Path, default=None, help="Write report to file.")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


def run_benchmark(
    index: QuantumRAGIndex,
    benchmark: list[dict],
    *,
    top_k: int,
    alpha: float,
    verbose: bool,
) -> dict:
    query_results = []
    total_rr = 0.0
    hits_at_k = 0

    for query_spec in benchmark:
        query = query_spec["query"]
        expected = query_spec["expected_source_substrings"]

        t0 = time.monotonic()
        results = retrieve(index, query, top_k=top_k, alpha=alpha)
        elapsed_ms = (time.monotonic() - t0) * 1000

        sources = [r.chunk.source_path for r in results]
        rr = 0.0
        first_hit_rank = None
        for i, src in enumerate(sources):
            if any(exp in src for exp in expected):
                rr = 1.0 / (i + 1)
                first_hit_rank = i + 1
                break

        hit = first_hit_rank is not None
        total_rr += rr
        hits_at_k += int(hit)

        entry = {
            "id": query_spec.get("id", ""),
            "query": query,
            "reciprocal_rank": rr,
            "hit": hit,
            "first_hit_rank": first_hit_rank,
            "latency_ms": round(elapsed_ms, 1),
            "top_sources": [
                {
                    "rank": r.rank,
                    "source": r.chunk.source_path,
                    "score": round(r.final_score, 4),
                }
                for r in results[:3]
            ],
        }
        query_results.append(entry)

        if verbose:
            status = f"RR={rr:.3f}" if rr < 1.0 else "✓"
            print(f"  {query_spec.get('id', '?'):40s} {status:8s} {elapsed_ms:6.1f}ms")

    n = len(benchmark)
    return {
        "index": None,  # filled by caller
        "benchmark": None,
        "num_queries": n,
        "top_k": top_k,
        "alpha": alpha,
        "hit_at_k": round(hits_at_k / n, 4) if n else 0,
        "mrr": round(total_rr / n, 4) if n else 0,
        "mean_latency_ms": round(
            sum(q["latency_ms"] for q in query_results) / n, 1
        ) if n else 0,
        "queries": query_results,
    }


def main() -> int:
    args = parse_args()

    if not args.index.exists():
        print(f"Index not found: {args.index}", file=sys.stderr)
        print("Run: python3 scripts/build_quantum_rag.py", file=sys.stderr)
        return 1

    if not args.benchmark.exists():
        print(f"Benchmark not found: {args.benchmark}", file=sys.stderr)
        return 1

    index = QuantumRAGIndex.load(args.index)
    benchmark = json.loads(args.benchmark.read_text(encoding="utf-8"))

    if args.verbose:
        summary = index.summary()
        print(f"Index: {args.index.name} ({summary['chunk_count']} chunks, {summary['source_count']} sources)")
        print(f"Benchmark: {args.benchmark.name} ({len(benchmark)} queries)")
        print()

    report = run_benchmark(
        index,
        benchmark,
        top_k=args.top_k,
        alpha=args.alpha,
        verbose=args.verbose,
    )
    report["index"] = str(args.index)
    report["benchmark"] = str(args.benchmark)

    if args.verbose:
        print()

    if args.json or args.output:
        report_json = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report_json + "\n", encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(report_json)
    else:
        print(f"hit@{args.top_k} = {report['hit_at_k']:.3f}")
        print(f"MRR     = {report['mrr']:.3f}")
        print(f"latency = {report['mean_latency_ms']:.1f}ms (mean)")
        misses = [q for q in report["queries"] if q["reciprocal_rank"] < 1.0]
        if misses:
            print(f"\nQueries not at rank 1 ({len(misses)}):")
            for q in misses:
                print(f"  {q['id']}: RR={q['reciprocal_rank']:.3f}, rank={q['first_hit_rank']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a low-compute hybrid RAG index for the quantum-gpt workspace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag import QuantumRAGIndex, build_chunks_from_roots


AUTHORITATIVE_ROOTS = [
    "AGENTS.md",
    "HEARTBEAT.md",
    "PROJECT.md",
    "TOOLS.md",
    "evals/benchmarks",
    "evals/tasks",
    "training",
    "scripts",
    "research/quantum_rag_low_compute.md",
    "research/model-target.md",
    "research/eval-spec-v0.md",
    "research/eval-difficulty-jump-v2.md",
]

BROAD_EXTRA_ROOTS = [
    "reports",
    "research",
]

# Curated quantum-computing algorithm and SDK documentation, intended
# specifically for grounding code-generation queries about quantum
# algorithms, gates, libraries and repair patterns.
QUANTUM_DOCS_ROOTS = [
    "docs/quantum_libraries",
]

PROFILE_ROOTS = {
    "authoritative": AUTHORITATIVE_ROOTS,
    "broad": AUTHORITATIVE_ROOTS + BROAD_EXTRA_ROOTS,
    # Docs-only profile: only the curated quantum library docs. Best for
    # measuring the marginal value of clean reference docs without any
    # repository self-leakage from evals/tasks or benchmarks.
    "quantum_docs": QUANTUM_DOCS_ROOTS,
    # Full quantum-code RAG profile: docs + the project's authoritative
    # operational notes (no eval task/test files, no reports), to give
    # the model both reference docs and project-specific conventions
    # without leaking the candidate.py reference implementations.
    "quantum_code": QUANTUM_DOCS_ROOTS + [
        "AGENTS.md",
        "HEARTBEAT.md",
        "PROJECT.md",
        "TOOLS.md",
        "research/quantum_rag_low_compute.md",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        default=[],
        help="Root file or directory to index. May be passed multiple times.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_ROOTS),
        default="authoritative",
        help="Named corpus profile to use when --root is not specified.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "index.pkl.gz",
    )
    parser.add_argument("--chunk-size", type=int, default=1400)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--min-chunk-chars", type=int, default=250)
    parser.add_argument("--dense-components", type=int, default=192)
    parser.add_argument("--max-features", type=int, default=50000)
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--summary-json", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected_roots = args.roots or PROFILE_ROOTS[args.profile]
    roots = [Path(item) for item in selected_roots]
    resolved_roots = [(ROOT / root).resolve() if not root.is_absolute() else root for root in roots]

    chunks = build_chunks_from_roots(
        resolved_roots,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_chars=args.min_chunk_chars,
        max_files=args.max_files,
    )
    if not chunks:
        raise SystemExit("No chunks were built. Check the provided roots or filters.")

    index = QuantumRAGIndex.build(
        chunks,
        max_features=args.max_features,
        dense_components=args.dense_components,
    )
    index.save(args.output)

    summary = {
        "output": str(args.output),
        "profile": args.profile,
        "roots": [path.as_posix() for path in resolved_roots],
        **index.summary(),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

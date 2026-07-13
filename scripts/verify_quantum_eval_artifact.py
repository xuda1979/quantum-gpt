#!/usr/bin/env python3
"""Verify and summarize the current quantum coding eval artifact.

This is intentionally small: it answers whether a benchmark artifact is a
credible holdout for base-vs-trained checkpoint comparisons without launching
models or touching training infrastructure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag import QuantumRAGIndex, build_chunks_from_roots
from scripts.check_benchmark_dataset_consistency import (
    discover_task_ids,
    load_benchmark_task_ids,
    summarize_manifest,
)
from scripts.check_quantum_task_rag_grounding import (
    TaskDescriptor,
    check_task_grounding,
    load_tasks,
)

DEFAULT_BENCHMARK = ROOT / "evals" / "benchmarks" / "qwen36_27b_quantum_holdout_v1.txt"
DEFAULT_ARTIFACT_MANIFEST = (
    ROOT / "data" / "generated" / "qwen36-27b-quantum-test-artifacts" / "manifest.json"
)
DEFAULT_SOURCE_MANIFEST = (
    ROOT / "data" / "generated" / "qwen36-27b-domain-expert-curriculum-v1" / "manifest.json"
)
DEFAULT_TASKS_ROOT = ROOT / "evals" / "tasks"
DEFAULT_DOC_ROOT = ROOT / "docs" / "quantum_libraries"

EXPECTED_DOC_FRAGMENTS = {
    "quantum_binary_measurement_decoder": "binary_measurement_decoders.md",
    "quantum_channel_depolarizing": "depolarizing_channel.md",
    "quantum_density_matrix_partial_trace": "density_matrix_eval_api.md",
    "quantum_ghz_state_witness": "ghz_state.md",
    "quantum_grover_oracle_diffusion": "grover_search.md",
    "quantum_phase_register_roundtrip": "quantum_phase_estimation.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-file", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--artifact-manifest", type=Path, default=DEFAULT_ARTIFACT_MANIFEST)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--doc-root", type=Path, default=DEFAULT_DOC_ROOT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--min-task-count", type=int, default=6)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _task_index(tasks_root: Path) -> dict[str, TaskDescriptor]:
    return {task.task_id: task for task in load_tasks(tasks_root / "quantum")}


def _build_docs_index(doc_root: Path) -> QuantumRAGIndex:
    chunks = build_chunks_from_roots(
        [doc_root], chunk_size=1200, chunk_overlap=160, min_chunk_chars=80
    )
    if not chunks:
        raise ValueError(f"No quantum docs chunks built from {doc_root}")
    return QuantumRAGIndex.build(chunks, max_features=512, dense_components=8)


def _doc_grounding(task_ids: list[str], *, tasks_root: Path, doc_root: Path) -> dict[str, Any]:
    task_index = _task_index(tasks_root)
    docs_index = _build_docs_index(doc_root)

    results: dict[str, Any] = {}
    grounded_count = 0
    expected_source_hits = 0
    for task_id in task_ids:
        task = task_index.get(task_id)
        if task is None:
            results[task_id] = {
                "grounded": False,
                "expected_source_hit": False,
                "error": "missing task",
            }
            continue
        result = check_task_grounding(
            task,
            index=docs_index,
            top_k=3,
            alpha=0.55,
            min_score=0.1,
            min_matched_terms=1,
            max_chunks_per_source=1,
        )
        expected_fragment = EXPECTED_DOC_FRAGMENTS.get(task_id)
        expected_hit = bool(
            expected_fragment and any(expected_fragment in hit.source_path for hit in result.hits)
        )
        grounded_count += int(result.grounded)
        expected_source_hits += int(expected_hit)
        results[task_id] = {
            "grounded": result.grounded,
            "best_score": result.best_score,
            "matched_terms": result.matched_terms,
            "expected_source_fragment": expected_fragment,
            "expected_source_hit": expected_hit,
            "top_sources": [hit.source_path for hit in result.hits],
        }

    return {
        "grounded_count": grounded_count,
        "expected_source_hits": expected_source_hits,
        "results": results,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    benchmark_task_ids = load_benchmark_task_ids(args.benchmark_file)
    known_tasks = discover_task_ids(args.tasks_root)
    missing_task_ids = [task_id for task_id in benchmark_task_ids if task_id not in known_tasks]

    artifact_manifest = load_json(args.artifact_manifest)
    source_manifest = load_json(args.source_manifest)
    artifact_contract = artifact_manifest.get("dataset_contract", {})
    source_summary = summarize_manifest(source_manifest)

    benchmark_set = set(benchmark_task_ids)
    artifact_eval_ids = set(artifact_contract.get("eval_task_ids", []))
    artifact_train_ids = set(artifact_contract.get("train_task_ids", []))
    source_train_ids = source_summary["train_task_ids"]
    source_eval_ids = source_summary["eval_task_ids"]

    doc_grounding = _doc_grounding(
        benchmark_task_ids, tasks_root=args.tasks_root, doc_root=args.doc_root
    )

    checks = {
        "task_count_meets_min": len(benchmark_task_ids) >= args.min_task_count,
        "all_benchmark_tasks_resolve": not missing_task_ids,
        "artifact_eval_matches_benchmark": artifact_eval_ids == benchmark_set,
        "artifact_train_excludes_benchmark": not (artifact_train_ids & benchmark_set),
        "source_train_excludes_benchmark": not (source_train_ids & benchmark_set),
        "source_eval_excludes_benchmark": not (source_eval_ids & benchmark_set),
        "docs_grounded": doc_grounding["grounded_count"] == len(benchmark_task_ids),
        "expected_doc_sources_hit": doc_grounding["expected_source_hits"]
        == len(benchmark_task_ids),
    }

    return {
        "kind": "quantum_eval_artifact_verification",
        "recommendation": {
            "artifact": "qwen36_27b_quantum_holdout_v1",
            "benchmark_file": args.benchmark_file.relative_to(ROOT).as_posix(),
            "use_for": "Qwen3.6-27B base vs trained checkpoint quantum coding comparison",
            "reason": (
                "It is task-disjoint from the Qwen3.6 domain-expert curriculum, resolves to executable "
                "quantum eval tasks, and every task is grounded in curated local quantum docs."
            ),
        },
        "artifact_manifest": args.artifact_manifest.relative_to(ROOT).as_posix(),
        "source_manifest": args.source_manifest.relative_to(ROOT).as_posix(),
        "metrics": {
            "task_count": len(benchmark_task_ids),
            "artifact_train_task_overlap": len(artifact_train_ids & benchmark_set),
            "source_train_task_overlap": len(source_train_ids & benchmark_set),
            "source_eval_task_overlap": len(source_eval_ids & benchmark_set),
            "docs_grounded": doc_grounding["grounded_count"],
            "expected_doc_sources_hit": doc_grounding["expected_source_hits"],
        },
        "benchmark_task_ids": benchmark_task_ids,
        "missing_task_ids": missing_task_ids,
        "overlap": {
            "artifact_train": sorted(artifact_train_ids & benchmark_set),
            "source_train": sorted(source_train_ids & benchmark_set),
            "source_eval": sorted(source_eval_ids & benchmark_set),
        },
        "doc_grounding": doc_grounding["results"],
        "checks": checks,
        "ok": all(checks.values()),
    }


def main() -> int:
    args = parse_args()
    report = build_report(args)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

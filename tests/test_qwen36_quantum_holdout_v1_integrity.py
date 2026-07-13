from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from quantum_rag import QuantumRAGIndex, build_chunks_from_roots
from scripts.check_quantum_task_rag_grounding import (
    TaskDescriptor,
    check_task_grounding,
    load_tasks,
)

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "evals" / "benchmarks" / "qwen36_27b_quantum_holdout_v1.txt"
ARTIFACT_MANIFEST = (
    ROOT / "data" / "generated" / "qwen36-27b-quantum-test-artifacts" / "manifest.json"
)
CURRICULUM_MANIFEST = (
    ROOT / "data" / "generated" / "qwen36-27b-domain-expert-curriculum-v1" / "manifest.json"
)


def _load_task_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _task_index() -> dict[str, TaskDescriptor]:
    tasks_root = ROOT / "evals" / "tasks" / "quantum"
    tasks = load_tasks(tasks_root)
    return {task.task_id: task for task in tasks}


def _build_docs_index() -> QuantumRAGIndex:
    doc_root = ROOT / "docs" / "quantum_libraries"
    chunks = build_chunks_from_roots(
        [doc_root], chunk_size=1200, chunk_overlap=160, min_chunk_chars=80
    )
    return QuantumRAGIndex.build(chunks, max_features=512, dense_components=8)


def test_qwen36_quantum_holdout_benchmark_is_task_disjoint_and_resolves() -> None:
    benchmark_task_ids = _load_task_ids(BENCHMARK)
    assert benchmark_task_ids == [
        "quantum_density_matrix_partial_trace",
        "quantum_channel_depolarizing",
        "quantum_ghz_state_witness",
        "quantum_grover_oracle_diffusion",
        "quantum_phase_register_roundtrip",
        "quantum_binary_measurement_decoder",
    ]

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_benchmark_dataset_consistency.py"),
            "--benchmark-file",
            str(BENCHMARK),
            "--tasks-root",
            str(ROOT / "evals" / "tasks"),
            "--manifest",
            str(ARTIFACT_MANIFEST),
            "--require-all-benchmark-tasks-in-manifest-eval",
            "--require-benchmark-tasks-absent-from-manifest-train",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["manifest_overlap"]["benchmark_vs_train_task_ids"] == []
    assert set(payload["manifest_overlap"]["benchmark_vs_eval_task_ids"]) == set(benchmark_task_ids)

    curriculum = json.loads(CURRICULUM_MANIFEST.read_text(encoding="utf-8"))
    train_task_ids = set(curriculum["dataset_contract"]["train_task_ids"])
    assert not (set(benchmark_task_ids) & train_task_ids)


def test_qwen36_quantum_holdout_tasks_are_docs_grounded() -> None:
    task_index = _task_index()
    docs_index = _build_docs_index()
    expected_docs = {
        "quantum_density_matrix_partial_trace": "density_matrix_eval_api.md",
        "quantum_channel_depolarizing": "depolarizing_channel.md",
        "quantum_ghz_state_witness": "ghz_state.md",
        "quantum_grover_oracle_diffusion": "grover_search.md",
        "quantum_phase_register_roundtrip": "quantum_phase_estimation.md",
        "quantum_binary_measurement_decoder": "binary_measurement_decoders.md",
    }

    grounded = []
    for task_id, doc_fragment in expected_docs.items():
        task = task_index[task_id]
        result = check_task_grounding(
            task,
            index=docs_index,
            top_k=3,
            alpha=0.55,
            min_score=0.1,
            min_matched_terms=1,
            max_chunks_per_source=1,
        )
        assert result.grounded, task_id
        assert any(doc_fragment in hit.source_path for hit in result.hits), task_id
        assert any(result.matched_terms), task_id
        grounded.append(task_id)

    assert grounded == list(expected_docs)


def test_qwen36_quantum_holdout_quality_report_matches_artifact() -> None:
    payload = json.loads(
        (ROOT / "reports" / "qwen36_27b_quantum_holdout_v1_quality.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["ok"] is True
    assert payload["metrics"]["task_count"] == 6
    assert payload["metrics"]["train_task_overlap"] == 0
    assert payload["metrics"]["docs_grounded"] == 6

from __future__ import annotations

import json
from pathlib import Path

from quantum_rag import QuantumRAGIndex, build_chunks_from_roots
from scripts.check_quantum_task_rag_grounding import (
    TaskDescriptor,
    build_report,
    build_task_query,
    check_task_grounding,
    expected_terms,
    load_tasks,
)


def _write_task(root: Path, task_id: str, name: str, category: str = "algorithm") -> Path:
    task_dir = root / task_id.replace("quantum_", "")
    task_dir.mkdir(parents=True)
    task_json = task_dir / "task.json"
    task_json.write_text(
        json.dumps(
            {
                "id": task_id,
                "name": name,
                "domain": "quantum",
                "category": category,
                "candidate_file": "candidate.py",
                "test_file": "tests.py",
            }
        ),
        encoding="utf-8",
    )
    return task_json


def _build_tiny_index(doc_root: Path) -> QuantumRAGIndex:
    chunks = build_chunks_from_roots(
        [doc_root],
        chunk_size=500,
        chunk_overlap=50,
        min_chunk_chars=20,
    )
    return QuantumRAGIndex.build(chunks, max_features=512, dense_components=8)


def test_load_tasks_reads_quantum_task_json_only(tmp_path: Path) -> None:
    task_root = tmp_path / "evals" / "tasks" / "quantum"
    task_path = _write_task(task_root, "quantum_qaoa_maxcut", "QAOA MaxCut")
    non_quantum = task_root / "software_like"
    non_quantum.mkdir()
    (non_quantum / "task.json").write_text(
        json.dumps({"id": "software_config_merge", "domain": "software", "name": "Config merge"}),
        encoding="utf-8",
    )

    tasks = load_tasks(task_root)

    assert tasks == [
        TaskDescriptor(
            task_id="quantum_qaoa_maxcut",
            name="QAOA MaxCut",
            category="algorithm",
            task_path=task_path.as_posix(),
        )
    ]


def test_task_query_and_terms_preserve_quantum_keywords() -> None:
    task = TaskDescriptor(
        task_id="quantum_phase_estimation_circuit",
        name="Phase estimation circuit",
        category="algorithm_reasoning",
        task_path="task.json",
    )

    assert "phase estimation circuit" in build_task_query(task)
    assert {"phase", "estimation", "circuit", "algorithm"} <= set(expected_terms(task))
    assert "quantum" not in expected_terms(task)


def test_check_task_grounding_finds_relevant_authoritative_doc(tmp_path: Path) -> None:
    doc_root = tmp_path / "docs"
    doc_root.mkdir()
    (doc_root / "qaoa_maxcut.md").write_text(
        "QAOA MaxCut uses a cost Hamiltonian, mixer Hamiltonian, weighted edges, "
        "and bitstring cut evaluation.",
        encoding="utf-8",
    )
    (doc_root / "teleportation.md").write_text(
        "Quantum teleportation uses Bell measurement and Pauli corrections.",
        encoding="utf-8",
    )
    index = _build_tiny_index(doc_root)
    task = TaskDescriptor(
        task_id="quantum_qaoa_maxcut",
        name="QAOA MaxCut cost function",
        category="algorithm_implementation",
        task_path="task.json",
    )

    result = check_task_grounding(
        task,
        index=index,
        top_k=2,
        alpha=0.55,
        min_score=0.1,
        min_matched_terms=1,
        max_chunks_per_source=1,
    )

    assert result.grounded
    assert "qaoa" in result.matched_terms
    assert result.hits[0].source_path.endswith("qaoa_maxcut.md")


def test_check_task_grounding_marks_missing_when_docs_do_not_match(tmp_path: Path) -> None:
    doc_root = tmp_path / "docs"
    doc_root.mkdir()
    (doc_root / "teleportation.md").write_text(
        "Quantum teleportation uses Bell measurement and Pauli corrections.",
        encoding="utf-8",
    )
    index = _build_tiny_index(doc_root)
    task = TaskDescriptor(
        task_id="quantum_trotterized_hamiltonian_evolution",
        name="Trotterized Hamiltonian evolution",
        category="algorithm_implementation",
        task_path="task.json",
    )

    result = check_task_grounding(
        task,
        index=index,
        top_k=1,
        alpha=0.55,
        min_score=0.1,
        min_matched_terms=1,
        max_chunks_per_source=1,
    )

    assert not result.grounded
    assert result.matched_terms == []


def test_build_report_summarizes_missing_tasks() -> None:
    grounded = TaskDescriptor(
        task_id="quantum_qaoa_maxcut",
        name="QAOA MaxCut",
        category="algorithm",
        task_path="a/task.json",
    )
    missing = TaskDescriptor(
        task_id="quantum_unknown",
        name="Unknown task",
        category="algorithm",
        task_path="b/task.json",
    )
    # Keep the summary assertion independent of retrieval internals.
    from scripts.check_quantum_task_rag_grounding import TaskGroundingResult

    report = build_report(
        [
            TaskGroundingResult(
                task_id=grounded.task_id,
                name=grounded.name,
                category=grounded.category,
                task_path=grounded.task_path,
                query="qaoa",
                grounded=True,
                best_score=1.0,
                matched_terms=["qaoa"],
                hits=[],
            ),
            TaskGroundingResult(
                task_id=missing.task_id,
                name=missing.name,
                category=missing.category,
                task_path=missing.task_path,
                query="unknown",
                grounded=False,
                best_score=0.0,
                matched_terms=[],
                hits=[],
            ),
        ],
        task_root=Path("evals/tasks/quantum"),
        doc_roots=[Path("docs/quantum_libraries")],
        top_k=3,
        alpha=0.55,
        min_score=0.35,
        min_matched_terms=1,
        index_summary={"chunk_count": 2},
    )

    assert report["ok"] is False
    assert report["metrics"]["grounded_tasks"] == 1
    assert report["missing_task_ids"] == ["quantum_unknown"]

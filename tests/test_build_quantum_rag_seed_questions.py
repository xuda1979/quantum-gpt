from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import build_quantum_rag_seed_questions as builder


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_build_records_from_quantum_docs_have_seed_contract() -> None:
    records = builder.build_records()

    source_docs = sorted(path for path in builder.DEFAULT_DOCS_DIR.glob("*.md") if path.name != "README.md")
    assert len(records) == len(source_docs)
    assert len({record["example_id"] for record in records}) == len(records)
    assert {record["format"] for record in records} == {"chat-sft-v1"}
    assert {record["source_schema"] for record in records} == {"quantum-rag-seed-questions-v1"}

    source_paths = {record["metadata"]["source_path"] for record in records}
    assert "docs/quantum_libraries/qiskit_basics.md" in source_paths
    assert "docs/quantum_libraries/qaoa_maxcut.md" in source_paths
    assert not any(path.startswith("evals/") for path in source_paths)

    frameworks = {record["metadata"]["target_framework"] for record in records}
    categories = {record["metadata"]["category"] for record in records}
    task_types = {record["metadata"]["task_type"] for record in records}

    assert {"qiskit", "cirq", "pennylane", "braket", "numpy"} <= frameworks
    assert {"algorithm_implementation", "circuit_construction", "state_simulation"} <= categories
    assert {"implementation", "repair"} <= task_types

    for record in records:
        metadata = record["metadata"]
        assert [message["role"] for message in record["messages"]] == ["system", "user", "assistant"]
        assert metadata["source"] == "docs_quantum_libraries"
        assert metadata["source_path"].startswith("docs/quantum_libraries/")
        assert metadata["source_doc_sha256"]
        assert metadata["holdout_policy"] == "source_docs_only_no_eval_holdout_files"
        assert metadata["numeric_boundary"] == "doc_grounded_no_fabricated_results"
        assert "fabricate" in record["messages"][2]["content"].lower()


def test_cli_writes_seed_questions_and_manifest(tmp_path: Path) -> None:
    output = tmp_path / "quantum_rag_seed_questions.jsonl"
    manifest_path = tmp_path / "quantum_rag_seed_questions_manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_quantum_rag_seed_questions.py"),
            "--output",
            str(output),
            "--manifest",
            str(manifest_path),
        ],
        cwd=ROOT,
        check=True,
    )

    records = load_jsonl(output)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(records) == manifest["summary"]["count"]
    assert manifest["manifest_version"] == "quantum-rag-seed-questions-v1"
    assert manifest["holdout_policy"] == "source_docs_only_no_eval_holdout_files"
    assert "docs/quantum_libraries/qiskit_basics.md" in manifest["summary"]["source_paths"]


def test_reject_holdout_or_eval_source_paths() -> None:
    with pytest.raises(ValueError, match="holdout/eval"):
        builder.reject_holdout_path(ROOT / "evals" / "benchmarks" / "quantum_generalization_holdout_v1.txt")

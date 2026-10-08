from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import build_quantum_distillation_seed_questions as builder

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_build_records_from_rag_docs_have_asi2_distillation_contract() -> None:
    records = builder.build_records(max_source_docs=40)

    assert len(records) == 160
    assert len({record["example_id"] for record in records}) == len(records)
    assert {record["schema_version"] for record in records} == {"dataset-v0"}
    assert {record["metadata"]["target_env"] for record in records} == {"ASI2"}
    assert {record["metadata"]["student_model"] for record in records} == {"Qwen/Qwen3.6-35B-A3B"}
    assert {record["metadata"]["teacher_model"] for record in records} == {"DeepSeek-v4-pro"}
    assert {record["metadata"]["distillation_strategy"] for record in records} == {
        "hard_sft_black_box_teacher"
    }
    assert {"implementation", "repair", "agentic_trajectory", "optimization"} <= {
        record["task_type"] for record in records
    }

    source_paths = {record["metadata"]["source_path"] for record in records}
    assert any(path.startswith("docs/quantum_libraries/") for path in source_paths)
    assert any(path.startswith("docs/external/quantum-sdk-docs-latest/") for path in source_paths)
    assert not any(".css-" in path for path in source_paths)
    assert not any("_static" in path or "_modules" in path for path in source_paths)
    assert not any(path.startswith("evals/") for path in source_paths)

    for record in records:
        assert record["domain"] == "quantum"
        assert record["source"] == "rag_docs_quantum_distillation_seed"
        assert record["instruction"].strip()
        assert record["response"].strip()
        assert "RAG excerpt" in record["response"]
        assert "<think>" not in record["response"].lower()
        assert (
            record["artifacts"]["teacher_prompt_policy"]
            == "concise_rationale_summary_plus_final_answer"
        )
        assert record["metadata"]["holdout_policy"] == "rag_docs_only_no_eval_holdout_files"


def test_cli_writes_dataset_v0_and_manifest(tmp_path: Path) -> None:
    output = tmp_path / "distill.jsonl"
    manifest_path = tmp_path / "manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_quantum_distillation_seed_questions.py"),
            "--output",
            str(output),
            "--manifest",
            str(manifest_path),
            "--max-source-docs",
            "8",
            "--variants-per-doc",
            "2",
        ],
        cwd=ROOT,
        check=True,
    )

    records = load_jsonl(output)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(records) == 16
    assert manifest["manifest_version"] == "quantum-distillation-seed-questions-asi2-v1"
    assert manifest["summary"]["count"] == 16
    assert manifest["summary"]["target_env"] == "ASI2"
    assert manifest["summary"]["distillation_strategy"] == "hard_sft_black_box_teacher"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_dataset_v0.py"),
            "--input-jsonl",
            str(output),
            "--min-count",
            "16",
        ],
        cwd=ROOT,
        check=True,
    )


def test_reject_holdout_or_eval_source_paths() -> None:
    with pytest.raises(ValueError, match="holdout/eval"):
        builder.reject_holdout_path(
            ROOT / "evals" / "tasks" / "quantum" / "bell_pair_construction" / "tests.py"
        )

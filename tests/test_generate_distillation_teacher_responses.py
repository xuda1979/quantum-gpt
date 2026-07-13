from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_distillation_teacher_responses as generator


def seed_row() -> dict:
    return {
        "schema_version": "dataset-v0",
        "example_id": "asi2_distill_bell_implementation_01",
        "domain": "quantum",
        "category": "quantum_engineering",
        "task_type": "implementation",
        "source": "rag_docs_quantum_distillation_seed",
        "difficulty": "medium",
        "language": "python",
        "framework": "qiskit",
        "tags": ["asi2", "rag"],
        "instruction": "Generate a Bell-pair coding task.",
        "response": "Teacher-response contract with RAG excerpt.",
        "artifacts": {"rag_excerpt": "Apply H to qubit 0 then CNOT 0->1."},
        "metadata": {
            "source_title": "Bell pair construction",
            "teacher_model": "DeepSeek-v4-flash",
            "student_model": "Qwen/Qwen3.6-35B-A3B",
            "target_env": "ASI2",
        },
    }


def test_parse_teacher_json_accepts_plain_or_fenced_json() -> None:
    payload = {
        "user_instruction": "Write code.",
        "teacher_response": "Rationale: short.\n\n```python\npass\n```",
    }
    text = json.dumps(payload)
    assert generator.parse_teacher_json(text) == payload
    assert generator.parse_teacher_json(f"```json\n{text}\n```") == payload


def test_parse_teacher_json_rejects_hidden_cot_tags() -> None:
    with pytest.raises(ValueError, match="think tag"):
        generator.parse_teacher_json(
            json.dumps({"user_instruction": "x", "teacher_response": "<think>secret</think>"})
        )


def test_build_user_prompt_contains_rag_and_contract() -> None:
    prompt = generator.build_user_prompt(seed_row())
    assert "Bell pair construction" in prompt
    assert "Apply H to qubit 0" in prompt
    assert "Teacher-response contract" in prompt


def test_build_sft_row_preserves_dataset_v0_contract() -> None:
    raw = {
        "model": "deepseek-v4-flash",
        "choices": [{"finish_reason": "stop"}],
        "usage": {"total_tokens": 123},
    }
    row = generator.build_sft_row(
        seed_row(),
        {
            "user_instruction": "Implement bell_pair_state().",
            "teacher_response": "Rationale: use documented amplitudes.\n\n```python\npass\n```",
        },
        raw,
    )
    assert row["schema_version"] == "dataset-v0"
    assert row["example_id"] == "asi2_distill_bell_implementation_01_teacher"
    assert row["instruction"] == "Implement bell_pair_state()."
    assert row["metadata"]["seed_example_id"] == "asi2_distill_bell_implementation_01"
    assert row["metadata"]["distillation_phase"] == "teacher_response_generation"
    assert row["metadata"]["teacher_api_model"] == "deepseek-v4-flash"
    assert "hard_sft" in row["tags"]


def test_read_completed_ids_tracks_seed_ids(tmp_path: Path) -> None:
    path = tmp_path / "out.jsonl"
    path.write_text(
        json.dumps({"metadata": {"seed_example_id": "seed_a"}}) + "\n", encoding="utf-8"
    )
    assert generator.read_completed_ids(path) == {"seed_a"}

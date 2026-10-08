from __future__ import annotations

from scripts import convert_dataset_v0_to_chat_sft as converter


def test_convert_row_to_chat_sft_v1() -> None:
    row = {
        "schema_version": "dataset-v0",
        "example_id": "ex1",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "task_type": "implementation",
        "source": "deepseek_teacher_hard_sft_from_rag_seed",
        "difficulty": "hard",
        "language": "python",
        "framework": "qiskit",
        "tags": ["rag"],
        "instruction": "Build a circuit.",
        "response": "Use H then CX.",
        "artifacts": {},
        "metadata": {"target_env": "ASI2"},
    }
    out = converter.convert_row(row, system_prompt="system", source_schema="dataset-v0")
    assert out["format"] == "chat-sft-v1"
    assert out["example_id"] == "ex1"
    assert out["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "Build a circuit."},
        {"role": "assistant", "content": "Use H then CX."},
    ]
    assert out["metadata"]["target_env"] == "ASI2"
    assert out["metadata"]["domain"] == "quantum"
    assert out["metadata"]["framework"] == "qiskit"


def test_append_question_suffix_is_identity() -> None:
    from scripts.prepare_isq_cot_sft_split import append_question_suffix

    prompt = "Explain the circuit."
    augmented = append_question_suffix(prompt)
    assert augmented.endswith("写成完整的可执行的代码。")
    assert prompt in augmented
    assert append_question_suffix(augmented) == augmented

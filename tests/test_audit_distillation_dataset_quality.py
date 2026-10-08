from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def row(example_id: str, task_type: str, category: str, framework: str, source: str) -> dict:
    return {
        "example_id": example_id,
        "domain": "quantum",
        "category": category,
        "task_type": task_type,
        "framework": framework,
        "instruction": "Implement a quantum circuit function and include tests for the qubit state behavior.",
        "response": "Rationale: first construct the quantum circuit, then use a lightweight check to validate the output.```python\nassert True\n```",
        "metadata": {
            "seed_example_id": example_id.replace("_teacher", ""),
            "source_doc_sha256": source,
            "category": category,
            "task_type": task_type,
            "framework": framework,
        },
    }


def test_audit_cli_rejects_split_packaging_gap(tmp_path: Path) -> None:
    task_types = ["implementation", "repair", "agentic_trajectory", "optimization"]
    categories = [
        "algorithm_implementation",
        "library_api_grounding",
        "hardware_compilation",
        "noise_and_mitigation",
        "quantum_engineering",
    ]
    frameworks = ["qiskit", "cirq", "pennylane", "braket", "cuda-quantum", "pyzx"]
    rows = [
        row(
            f"ex_{index}",
            task_types[index % 4],
            categories[index % 5],
            frameworks[index % 6],
            f"doc_{index}",
        )
        for index in range(12)
    ]
    chat_rows = [
        {
            "format": "chat-sft-v1",
            "example_id": item["example_id"],
            "messages": [],
            "metadata": item["metadata"],
        }
        for item in rows[:-1]
    ]

    seed = tmp_path / "seed.jsonl"
    generated = tmp_path / "generated.jsonl"
    chatml = tmp_path / "chatml.jsonl"
    split_dir = tmp_path / "split"
    write_jsonl(seed, rows)
    write_jsonl(generated, rows)
    write_jsonl(chatml, chat_rows)
    write_jsonl(split_dir / "train_chatml.jsonl", chat_rows[:8])
    write_jsonl(split_dir / "eval_chatml.jsonl", chat_rows[8:])

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "audit_distillation_dataset_quality.py"),
            "--seed-jsonl",
            str(seed),
            "--generated-jsonl",
            str(generated),
            "--chatml-jsonl",
            str(chatml),
            "--split-dir",
            str(split_dir),
            "--min-seed-rows",
            "12",
            "--min-generated-rows",
            "12",
            "--min-source-docs",
            "12",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "chatml ids do not match accepted generated ids" in result.stdout

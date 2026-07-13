from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import build_quantum_llm_plan_seed_dataset as builder

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_build_records_cover_plan_metadata_axes() -> None:
    records = builder.build_records()

    assert len(records) == 8
    assert len({record["example_id"] for record in records}) == len(records)
    assert {record["format"] for record in records} == {"chat-sft-v1"}
    assert {record["source_schema"] for record in records} == {"quantum-llm-plan-seed-v1"}

    output_types = {record["metadata"]["output_type"] for record in records}
    workflows = {record["metadata"]["workflow"] for record in records}
    frameworks = {record["metadata"]["target_framework"] for record in records}

    assert {"code", "formula", "structured_text", "refusal"} <= output_types
    assert {
        "problem_to_circuit",
        "circuit_to_code",
        "formula_to_code_skeleton",
        "error_repair",
        "research_workflow_decomposition",
        "refusal_numeric_boundary",
    } <= workflows
    assert {"qiskit", "cirq", "pennylane", None} <= frameworks

    for record in records:
        metadata = record["metadata"]
        assert builder.REQUIRED_METADATA_FIELDS <= set(metadata)
        assert [message["role"] for message in record["messages"]] == [
            "system",
            "user",
            "assistant",
        ]
        assert metadata["numeric_boundary"]
        assert metadata["target_framework"] == metadata["framework"]


def test_numeric_boundary_refusals_do_not_emit_fake_numbers() -> None:
    records = builder.build_records()
    refusal_records = [
        record for record in records if record["metadata"]["output_type"] == "refusal"
    ]

    assert len(refusal_records) >= 2
    for record in refusal_records:
        assistant = record["messages"][2]["content"].lower()
        assert "not invent" in assistant or "cannot provide" in assistant
        assert "code" in assistant or "script" in assistant
        assert record["metadata"]["workflow"] == "refusal_numeric_boundary"


def test_cli_writes_jsonl_and_manifest(tmp_path: Path) -> None:
    output = tmp_path / "seed.jsonl"
    manifest_path = tmp_path / "manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_quantum_llm_plan_seed_dataset.py"),
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

    assert len(records) == 8
    assert manifest["manifest_version"] == "quantum-llm-plan-seed-v1"
    assert manifest["summary"]["count"] == 8
    assert manifest["summary"]["output_type"]["refusal"] == 2
    assert manifest["summary"]["workflow"]["refusal_numeric_boundary"] == 2

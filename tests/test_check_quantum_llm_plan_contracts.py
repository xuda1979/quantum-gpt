from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_quantum_llm_plan_contracts import check_records, load_records


def _report(rows: list[dict], tmp_path: Path) -> dict:
    return check_records(rows, [], tmp_path / "fixture.jsonl", "jsonl")


def test_numeric_boundary_marker_required_for_inferred_boundary_case(tmp_path: Path) -> None:
    rows = [
        {
            "example_id": "marked",
            "tags": ["numeric-boundary"],
            "instruction": "Handle n=0 and max n inclusively.",
            "response": "Use explicit lower and upper bounds.",
        },
        {
            "example_id": "missing",
            "instruction": "Fix the off-by-one behavior for n=0 and n=1.",
            "response": "Clamp the lower bound.",
        },
    ]

    report = _report(rows, tmp_path)

    assert report["checks"]["numeric_boundary_marking_ok"] is False
    assert report["numeric_boundary"]["records_with_signal"] == 2
    assert report["numeric_boundary"]["missing_markers"] == [
        {"record_id": "missing", "reason": "numeric-boundary signal without marker"}
    ]


def test_provenance_passes_when_tool_and_model_material_are_separate(tmp_path: Path) -> None:
    rows = [
        {
            "example_id": "separate-fields",
            "external_tool_results": {"simulator": {"probability": 0.5}},
            "model_generated_code": "def build():\n    return 'circuit'\n",
        },
        {
            "example_id": "separate-segments",
            "segments": [
                {"source": "tool", "content": "shots=1024"},
                {"source": "model", "content": "Use the observed counts."},
            ],
        },
    ]

    report = _report(rows, tmp_path)

    assert report["checks"]["provenance_contract_ok"] is True
    assert report["provenance"]["records_requiring_distinction"] == 2
    assert report["provenance"]["failure_count"] == 0


def test_provenance_fails_for_unlabeled_tool_result_inside_answer(tmp_path: Path) -> None:
    rows = [
        {
            "example_id": "mixed",
            "answer": "tool result: counts={'00': 512}. Therefore return code below.",
        }
    ]

    report = _report(rows, tmp_path)

    assert report["checks"]["provenance_contract_ok"] is False
    assert report["provenance"]["failures"][0]["record_id"] == "mixed"


def test_structured_ir_strings_must_parse_as_json_object_or_array(tmp_path: Path) -> None:
    rows = [
        {
            "example_id": "good-ir",
            "structured_ir": '{"version": "plan-ir-v0", "steps": [{"op": "h", "target": 0}]}',
        },
        {
            "example_id": "bad-ir",
            "structured_ir": "{not json",
        },
    ]

    report = _report(rows, tmp_path)

    assert report["checks"]["structured_ir_parseability_ok"] is False
    assert report["structured_ir"]["present_count"] == 2
    assert report["structured_ir"]["parseable_count"] == 1
    assert report["structured_ir"]["failures"][0]["record_id"] == "bad-ir"


def test_load_records_accepts_jsonl_and_plain_text_candidate(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "records.jsonl"
    jsonl_path.write_text(
        json.dumps(
            {"example_id": "a", "tags": ["numeric-boundary"], "instruction": "n=0 edge case"}
        )
        + "\n",
        encoding="utf-8",
    )
    records, errors, input_kind = load_records(jsonl_path)
    assert errors == []
    assert input_kind == "jsonl"
    assert records[0]["example_id"] == "a"

    candidate_path = tmp_path / "candidate.py"
    candidate_path.write_text("def solve():\n    return 1\n", encoding="utf-8")
    records, errors, input_kind = load_records(candidate_path)
    assert errors == []
    assert input_kind == "plain_text"
    assert records[0]["candidate_text"].startswith("def solve")


def test_cli_writes_report_and_returns_nonzero_on_contract_failure(tmp_path: Path) -> None:
    input_path = tmp_path / "records.jsonl"
    output_path = tmp_path / "report.json"
    input_path.write_text(
        json.dumps({"example_id": "missing", "instruction": "Check n=0 off-by-one behavior."})
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_quantum_llm_plan_contracts.py",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["ok"] is False
    assert report["numeric_boundary"]["missing_marker_count"] == 1

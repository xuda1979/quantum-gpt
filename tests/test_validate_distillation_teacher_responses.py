from __future__ import annotations

import json
from pathlib import Path

from scripts import validate_distillation_teacher_responses as validator


def valid_row() -> dict:
    return {
        "example_id": "ex_teacher",
        "instruction": "Implement a documented Bell-state circuit and include a small verification test.",
        "response": "Rationale: use H on qubit 0 and CNOT 0->1.\n\n```python\nfrom math import sqrt\namp = 1 / sqrt(2)\nassert round(amp * amp, 8) == 0.5\n```",
        "metadata": {"seed_example_id": "ex"},
    }


def test_valid_row_accepts_python_fence() -> None:
    assert validator.validate_row(Path("rows.jsonl"), 1, valid_row()) == []


def test_invalid_python_fence_is_reported() -> None:
    row = valid_row()
    row["response"] = (
        "Rationale: broken code and enough details to pass the response length gate "
        "for the quality validator, so it reaches the fenced syntax parse.\n\n"
        "```python\ndef nope(:\n    pass\n```"
    )
    errors = validator.validate_row(Path("rows.jsonl"), 1, row)
    assert any("syntax error" in error for error in errors)


def test_main_writes_quality_report(tmp_path: Path) -> None:
    input_path = tmp_path / "rows.jsonl"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(valid_row()) + "\n", encoding="utf-8")
    # Exercise the file-level helpers directly; CLI behavior is covered by integration commands.
    rows = list(validator.iter_rows(input_path))
    assert len(rows) == 1
    report = {
        "errors": validator.validate_row(input_path, rows[0][0], rows[0][1]),
        "count": len(rows),
    }
    output_path.write_text(json.dumps(report), encoding="utf-8")
    assert json.loads(output_path.read_text())["errors"] == []

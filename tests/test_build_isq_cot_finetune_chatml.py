from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import build_isq_cot_finetune_chatml as builder

ROOT = Path(__file__).resolve().parents[1]


def test_clean_prompt_and_convert_row() -> None:
    row = {
        "task_id": "x",
        "dataset_index": 1,
        "task_type": "code_generation",
        "difficulty": "easy",
        "category": "graph_state_preparation",
        "concept_tags": ["isq"],
        "source": "qa_pipeline",
        "prompt": "Question: Use isQ to prepare a Bell pair.",
        "reference_solution": "import std;\nqbit q[2];\nprocedure main() { H(q[0]); CNOT(q[0], q[1]); M(q[0]); M(q[1]); }",
    }
    out = builder.convert_row(row)
    assert out["messages"][1]["content"].startswith("Use isQ")
    assert out["messages"][1]["content"].endswith(". Write the code using isQ language.")
    assert not out["messages"][1]["content"].lstrip().lower().startswith("question")
    assert out["messages"][2]["content"].startswith("import std;")


def test_cli_writes_finetune_file(tmp_path: Path) -> None:
    out = tmp_path / "finetune.jsonl"
    manifest = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_isq_cot_finetune_chatml.py"),
            "--output-jsonl",
            str(out),
            "--manifest",
            str(manifest),
        ],
        cwd=ROOT,
        check=True,
    )
    rows = [
        json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    meta = json.loads(manifest.read_text(encoding="utf-8"))
    assert len(rows) == 2595
    assert meta["rows"] == 2595
    assert meta["source_rows"] == 2595
    assert meta["all_prompts_cleaned"] is True
    assert meta["no_prompt_starts_with_question"] is True
    assert all(
        row["messages"][1]["content"].endswith(". Write the code using isQ language.")
        for row in rows[:20]
    )
    assert all(
        row["messages"][2]["content"].lstrip().startswith("import std;")
        or row["messages"][2]["content"].lstrip().startswith("//")
        for row in rows[:20]
    )
    assert meta["all_answers_full_code"] is True

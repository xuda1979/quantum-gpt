from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_task_subset_dataset_writes_dataset_contract(tmp_path: Path) -> None:
    input_path = tmp_path / "input.jsonl"
    task_id_file = tmp_path / "tasks.txt"
    out_dir = tmp_path / "out"

    input_rows = [
        {
            "example_id": "ex1",
            "messages": [],
            "metadata": {"task_id": "task_a", "domain": "quantum", "prompt_family": "family_a"},
        },
        {
            "example_id": "ex2",
            "messages": [],
            "metadata": {"task_id": "task_a", "domain": "quantum", "prompt_family": "family_b"},
        },
        {
            "example_id": "ex3",
            "messages": [],
            "metadata": {"task_id": "task_b", "domain": "software", "prompt_family": "family_c"},
        },
        {
            "example_id": "ex4",
            "messages": [],
            "metadata": {"task_id": "task_b", "domain": "software", "prompt_family": "family_d"},
        },
    ]
    input_path.write_text("".join(json.dumps(row) + "\n" for row in input_rows), encoding="utf-8")
    task_id_file.write_text("task_a\ntask_b\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_task_subset_dataset.py"),
            "--input",
            str(input_path),
            "--task-id-file",
            str(task_id_file),
            "--out-dir",
            str(out_dir),
            "--train-ratio",
            "0.5",
            "--seed-tag",
            "v1",
        ],
        cwd=ROOT,
        check=True,
    )

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    contract = manifest["dataset_contract"]
    assert contract["generation_script"] == "scripts/build_task_subset_dataset.py"
    assert sorted(contract["source_task_ids"]) == ["task_a", "task_b"]
    assert (
        sorted(contract["train_task_ids"] + contract["eval_task_ids"])
        == ["task_a", "task_a", "task_b", "task_b"][
            : len(contract["train_task_ids"]) + len(contract["eval_task_ids"])
        ]
    )
    assert "train" in contract["prompt_families"]
    assert "eval" in contract["prompt_families"]
    assert contract["benchmark_contracts"][0]["name"] == "selected_task_subset"

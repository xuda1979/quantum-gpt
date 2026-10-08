from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import build_isq_cot_finetune_split as split_builder

ROOT = Path(__file__).resolve().parents[1]


def test_clean_prompt_adds_required_suffix() -> None:
    prompt = "What is a Bell pair?"
    cleaned = split_builder.clean_prompt(prompt)
    assert cleaned.endswith(". Write the code using isQ language.")
    legacy = "What is a Bell pair? Write the code using isQ language. Return complete standalone runnable code."
    assert split_builder.clean_prompt(legacy).endswith(". Write the code using isQ language.")
    assert "Return complete standalone runnable code." not in split_builder.clean_prompt(legacy)


def test_cli_writes_train_test_split(tmp_path: Path) -> None:
    input_jsonl = tmp_path / "finetune.jsonl"
    manifest_json = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_isq_cot_finetune_chatml.py"),
            "--output-jsonl",
            str(input_jsonl),
            "--manifest",
            str(manifest_json),
        ],
        cwd=ROOT,
        check=True,
    )
    out_dir = tmp_path / "split"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_isq_cot_finetune_split.py"),
            "--input-jsonl",
            str(input_jsonl),
            "--output-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        check=True,
    )
    train = [
        json.loads(line)
        for line in (out_dir / "train_chatml.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    test = [
        json.loads(line)
        for line in (out_dir / "test_chatml.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert len(train) + len(test) == 2595
    assert len(train) == 2076
    assert len(test) == 519
    assert manifest["no_example_id_overlap"] is True
    assert manifest["all_answers_full_code"] is True
    assert all(
        row["messages"][1]["content"].endswith(". Write the code using isQ language.")
        for row in train[:10]
    )
    assert all(
        row["messages"][1]["content"].endswith(". Write the code using isQ language.")
        for row in test[:10]
    )
    assert all(
        row["messages"][2]["content"].lstrip().startswith("import std;")
        or row["messages"][2]["content"].lstrip().startswith("//")
        for row in train[:10]
    )

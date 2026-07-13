from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_build_curriculum_mix_dataset_filters_and_repeats(tmp_path: Path) -> None:
    train_a = tmp_path / "set_a_train.jsonl"
    train_b = tmp_path / "set_b_train.jsonl"
    eval_b = tmp_path / "set_b_eval.jsonl"
    exclude_tasks = tmp_path / "exclude.txt"
    out_dir = tmp_path / "out"

    write_jsonl(
        train_a,
        [
            {
                "example_id": "qa1",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "q_keep"},
            },
            {
                "example_id": "qa2",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "q_keep"},
            },
            {
                "example_id": "qa3",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "q_drop"},
            },
        ],
    )
    write_jsonl(
        train_b,
        [
            {
                "example_id": "sb1",
                "messages": [],
                "metadata": {"domain": "software", "task_id": "s_keep"},
            },
            {
                "example_id": "qb1",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "q_other"},
            },
        ],
    )
    write_jsonl(
        eval_b,
        [
            {
                "example_id": "se1",
                "messages": [],
                "metadata": {"domain": "software", "task_id": "s_eval"},
            },
        ],
    )
    exclude_tasks.write_text("q_drop\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_curriculum_mix_dataset.py"),
            "--train-source",
            f"{train_a}::label=quantum_train::exclude_task_file={exclude_tasks}",
            "--train-source",
            f"{train_b}::label=software_train::domain=software::repeat=2",
            "--eval-source",
            f"{eval_b}::label=software_eval::domain=software",
            "--out-dir",
            str(out_dir),
            "--seed-tag",
            "test-curriculum",
            "--require-train-domain-min",
            "quantum=2",
            "--require-train-domain-min",
            "software=2",
            "--require-eval-domain-ratio",
            "software=1.0",
            "--reference-note",
            "PDF: domain expert fine-tuning needs expert data plus replay coverage.",
        ],
        cwd=ROOT,
        check=True,
    )

    train_rows = [
        json.loads(line)
        for line in (out_dir / "train.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    eval_rows = [
        json.loads(line)
        for line in (out_dir / "eval.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))

    assert len(train_rows) == 4
    assert len(eval_rows) == 1
    assert {row["metadata"]["curriculum_source"] for row in train_rows} == {
        "quantum_train",
        "software_train",
    }
    assert all(row["metadata"]["domain"] in {"quantum", "software"} for row in train_rows)
    assert all(row["metadata"]["domain"] == "software" for row in eval_rows)
    assert not any(row["metadata"]["task_id"] == "q_drop" for row in train_rows)
    assert len({row["example_id"] for row in train_rows}) == len(train_rows)
    assert manifest["train_summary"]["count"] == 4
    assert manifest["eval_summary"]["count"] == 1
    assert (
        manifest["dataset_contract"]["generation_script"]
        == "scripts/build_curriculum_mix_dataset.py"
    )
    contract = manifest["domain_expert_contract"]
    assert contract["ok"] is True
    assert contract["contract_version"] == "domain-expert-curriculum-v1"
    assert contract["checks"]["train_domain_min_quantum"] is True
    assert contract["checks"]["train_domain_min_software"] is True
    assert contract["checks"]["eval_domain_ratio_software"] is True
    assert contract["reference_notes"] == [
        "PDF: domain expert fine-tuning needs expert data plus replay coverage."
    ]


def test_build_curriculum_mix_dataset_fails_domain_expert_gate(tmp_path: Path) -> None:
    train = tmp_path / "train.jsonl"
    eval_file = tmp_path / "eval.jsonl"
    out_dir = tmp_path / "out"
    write_jsonl(
        train,
        [
            {
                "example_id": "q1",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "q1"},
            },
        ],
    )
    write_jsonl(
        eval_file,
        [
            {
                "example_id": "e1",
                "messages": [],
                "metadata": {"domain": "quantum", "task_id": "e1"},
            },
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_curriculum_mix_dataset.py"),
            "--train-source",
            f"{train}::label=quantum_train",
            "--eval-source",
            f"{eval_file}::label=quantum_eval",
            "--out-dir",
            str(out_dir),
            "--require-train-domain-min",
            "software=1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Domain-expert curriculum gates failed" in result.stderr
    assert not (out_dir / "train.jsonl").exists()

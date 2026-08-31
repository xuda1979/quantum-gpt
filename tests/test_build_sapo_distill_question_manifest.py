from __future__ import annotations

import itertools
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def test_builder_selects_verified_diverse_disjoint_questions(tmp_path: Path) -> None:
    output = tmp_path / "manifest.txt"
    completed = subprocess.run(
        ["python3", "scripts/build_sapo_distill_question_manifest.py", "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    ids = _ids(output)

    assert report["targeted"] == 10
    assert report["deterministic"] == 0
    assert report["semantic"] == 64
    assert report["total"] == 74
    assert len(ids) == len(set(ids)) == 74
    assert len(report["frameworks"]) >= 4
    assert len(report["topics"]) >= 8
    assert "qc-0521" not in ids

    promotion = set()
    for name in (
        "quantum_generalization_holdout_v1.txt",
        "quantum_generalization_holdout_v2_hard.txt",
        "quantum_generalization_holdout_v3_multi_framework.txt",
        "qwen36_27b_quantum_holdout_v1.txt",
        "sapo_promotion_holdout_v1_18.txt",
    ):
        promotion.update(_ids(ROOT / "evals/benchmarks" / name))
    assert set(ids).isdisjoint(promotion)

    deterministic = set(_ids(ROOT / "evals/benchmarks/quantum_distill_v3_deterministic.txt"))
    semantic = set(_ids(ROOT / "evals/benchmarks/quantum_distill_v3_sampling.txt"))
    qc_ids = [task_id for task_id in ids if task_id.startswith("qc-")]
    assert sum(task_id in deterministic for task_id in qc_ids) == 0
    assert sum(task_id in semantic for task_id in qc_ids) == 64

    rows = [
        json.loads(line)
        for line in (
            ROOT
            / "data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v3/questions_and_code.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    questions = {f"qc-{index:04d}": row["question"] for index, row in enumerate(rows, 1)}

    def grams(text: str) -> set[tuple[str, ...]]:
        words = re.findall(r"[a-z_]+", text.lower())
        return {tuple(words[i : i + 4]) for i in range(max(0, len(words) - 3))}

    for left, right in itertools.combinations(qc_ids, 2):
        left_grams, right_grams = grams(questions[left]), grams(questions[right])
        similarity = len(left_grams & right_grams) / len(left_grams | right_grams)
        assert similarity < 0.82, (left, right, similarity)


def test_builder_filters_on_reference_imports_not_framework_name(tmp_path: Path) -> None:
    output = tmp_path / "runtime-manifest.txt"
    completed = subprocess.run(
        [
            "python3",
            "scripts/build_sapo_distill_question_manifest.py",
            "--output",
            str(output),
            "--semantic-count",
            "2",
            "--available-import-root",
            "numpy",
            "--available-import-root",
            "scipy",
            "--available-import-root",
            "qiskit",
            "--available-import-root",
            "qiskit_aer",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    declared = next(
        line
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.startswith("# required_import_roots=")
    )
    required = {root for root in declared.split("=", 1)[1].split(",") if root}
    assert required == set(report["required_import_roots"])
    assert required <= {"numpy", "scipy", "qiskit", "qiskit_aer"}
    assert report["runtime_rejected"] > 0

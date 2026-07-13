from __future__ import annotations

import json
from pathlib import Path

BENCHMARKS = Path("evals/benchmarks")
TRAINING_BM = BENCHMARKS / "quantum_grpo_training_v5_failure_shape_disjoint.txt"
HOLDOUT_BM = BENCHMARKS / "quantum_generalization_holdout_v1.txt"
TASKS_DIR = Path("evals/tasks/quantum")


def _load_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line)
    return ids


def test_v5_failure_shape_benchmark_exists() -> None:
    assert TRAINING_BM.exists(), f"Missing {TRAINING_BM}"


def test_v5_failure_shape_benchmark_tasks_exist_on_disk() -> None:
    task_ids = {
        json.loads((task_dir / "task.json").read_text(encoding="utf-8")).get("id", task_dir.name)
        for task_dir in TASKS_DIR.iterdir()
        if task_dir.is_dir() and (task_dir / "task.json").exists()
    }
    benchmark_ids = set(_load_ids(TRAINING_BM))
    missing = benchmark_ids - task_ids
    assert not missing, f"Tasks missing from v5 failure-shape benchmark: {sorted(missing)}"


def test_v5_failure_shape_benchmark_stays_disjoint_from_strict_holdout() -> None:
    training_ids = set(_load_ids(TRAINING_BM))
    holdout_ids = set(_load_ids(HOLDOUT_BM))
    overlap = training_ids & holdout_ids
    assert not overlap, f"v5 failure-shape benchmark overlaps strict holdout: {sorted(overlap)}"


def test_v5_failure_shape_benchmark_contains_new_exact_analogs() -> None:
    training_ids = set(_load_ids(TRAINING_BM))
    assert "quantum_gate_token_canonicalizer" in training_ids
    assert "quantum_binary_measurement_decoder" in training_ids
    assert "quantum_maxcut_assignment_enumerator" in training_ids
    assert "quantum_superdense_identity_lookup" in training_ids

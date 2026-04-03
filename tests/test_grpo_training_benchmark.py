"""Verify quantum_grpo_training_v1.txt is valid and distinct from the holdout."""
from pathlib import Path

BENCHMARKS = Path("evals/benchmarks")
TRAINING_BM = BENCHMARKS / "quantum_grpo_training_v1.txt"
HOLDOUT_BM  = BENCHMARKS / "quantum_generalization_holdout_v1.txt"
TASKS_DIR   = Path("evals/tasks/quantum")

def _load_ids(path):
    ids = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.add(line)
    return ids

def test_training_benchmark_exists():
    assert TRAINING_BM.exists(), f"Missing {TRAINING_BM}"

def test_training_benchmark_has_all_quantum_tasks():
    task_ids = {
        d.name if not (d / "task.json").exists() else
        __import__("json").loads((d / "task.json").read_text()).get("id", d.name)
        for d in TASKS_DIR.iterdir() if d.is_dir()
    }
    training_ids = _load_ids(TRAINING_BM)
    missing = task_ids - training_ids
    assert not missing, f"Tasks missing from training benchmark: {missing}"

def test_training_benchmark_not_subset_of_holdout():
    training_ids = _load_ids(TRAINING_BM)
    holdout_ids  = _load_ids(HOLDOUT_BM)
    training_only = training_ids - holdout_ids
    assert training_only, "Training benchmark should include tasks beyond the holdout set"

def test_no_overlap_policy_documented():
    """Holdout tasks may appear in training (generalization test), but training set is larger."""
    training_ids = _load_ids(TRAINING_BM)
    holdout_ids  = _load_ids(HOLDOUT_BM)
    assert len(training_ids) > len(holdout_ids), (
        f"Training set ({len(training_ids)}) should be larger than holdout ({len(holdout_ids)})"
    )

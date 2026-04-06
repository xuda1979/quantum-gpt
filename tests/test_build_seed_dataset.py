from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "data" / "seed" / "build_seed_dataset.py"
SPEC = importlib.util.spec_from_file_location("build_seed_dataset", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
build_seed_dataset = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_seed_dataset)


def test_build_example_defaults_missing_test_file_to_tests_py(tmp_path: Path) -> None:
    task_dir = tmp_path / "quantum" / "demo"
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": "quantum_demo",
                "name": "Quantum Demo",
                "domain": "quantum",
                "category": "smoke",
                "candidate_file": "candidate.py",
            }
        )
        + "\n"
    )
    (task_dir / "candidate.py").write_text("def solve() -> int:\n    return 1\n")
    (task_dir / "tests.py").write_text("def run_tests(candidate_path: str) -> dict:\n    return {'passed': True, 'details': ['ok']}\n")

    example = build_seed_dataset.build_example(
        {
            "task_dir": task_dir,
            "example_id": "quantum_demo_001",
            "task_type": "implementation",
            "source": "eval_derived",
            "difficulty": "easy",
            "framework": None,
            "tags": ["demo"],
            "instruction": "Solve the demo task.",
            "artifacts": ["tests", "reference_style"],
            "metadata": {},
        }
    )

    assert example["metadata"]["task_id"] == "quantum_demo"
    assert "def run_tests" in example["artifacts"]["tests"]

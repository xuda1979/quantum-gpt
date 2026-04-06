from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_TEST_FILE = "tests.py"


def resolve_test_path(task_dir: Path, metadata: dict[str, Any]) -> Path:
    test_file = metadata.get("test_file", DEFAULT_TEST_FILE)
    test_path = task_dir / test_file
    if not test_path.exists():
        task_id = metadata.get("id", task_dir.name)
        raise FileNotFoundError(f"Missing test file for task {task_id}: {test_path}")
    return test_path

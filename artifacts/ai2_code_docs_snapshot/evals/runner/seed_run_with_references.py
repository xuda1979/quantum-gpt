from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "evals" / "tasks"


def discover_tasks() -> list[Path]:
    return sorted(TASKS_ROOT.glob("*/*/task.json"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill a prepared eval run with bundled reference candidates.")
    parser.add_argument("run_dir", type=Path, help="Path to evals/runs/<run-id>")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    candidates_dir = run_dir / "candidates"
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates directory: {candidates_dir}")

    copied = 0
    for task_json in discover_tasks():
        task_dir = task_json.parent
        metadata = load_json(task_json)
        src = task_dir / metadata["candidate_file"]
        dst = candidates_dir / f"{metadata['id']}.py"
        dst.write_text(src.read_text())
        copied += 1

    print(f"Seeded {copied} candidate files in {run_dir.relative_to(ROOT)}")

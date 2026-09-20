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
    return json.loads(path.read_text(encoding="utf-8"))


def seed_candidates(run_dir: Path) -> int:
    """Copy declared candidate files into *run_dir*/candidates.

    Tasks whose task.json has no ``candidate_file`` key are silently skipped
    (by-design infra-only tasks).  Tasks that DECLARE a candidate_file but
    whose file is missing on disk raise ``SystemExit`` -- a silent skip would
    let a broken reference vanish from the baseline leg without trace.

    Returns the number of candidate files actually copied.
    """
    candidates_dir = run_dir / "candidates"
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates directory: {candidates_dir}")

    copied = 0
    for task_json in discover_tasks():
        task_dir = task_json.parent
        metadata = load_json(task_json)
        candidate_file = metadata.get("candidate_file")
        if candidate_file is None:
            continue
        src = task_dir / candidate_file
        if not src.exists():
            raise SystemExit(
                f"Task {metadata['id']} declares candidate_file "
                f"{candidate_file} but it does not exist at {src}"
            )
        dst = candidates_dir / f"{metadata['id']}.py"
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        copied += 1

    return copied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fill a prepared eval run with bundled reference candidates."
    )
    parser.add_argument("run_dir", type=Path, help="Path to evals/runs/<run-id>")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    copied = seed_candidates(run_dir)

    try:
        rel = run_dir.relative_to(ROOT)
    except ValueError:
        rel = run_dir
    print(f"Seeded {copied} candidate files in {rel}")

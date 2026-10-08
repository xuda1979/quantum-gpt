"""TDD: seed_run_with_references must skip by-design no-candidate tasks but
FAIL LOUDLY on a declared-but-missing reference.

2026-08-25 (QA sweep): the best-effort change treated both cases as a silent
skip — a task whose task.json DECLARES a candidate_file that is missing on
disk silently disappears from the seeded baseline leg (a partial baseline is
a wrong measurement). Undeclared (infra-only smoke tasks) = skip by design;
declared-but-missing = broken tree, fail closed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.seed_run_with_references import seed_candidates  # noqa: E402


def _make_task(tasks_root: Path, task_id: str, *, candidate: str | None) -> Path:
    task_dir = tasks_root / "q" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": task_id}
    if candidate is not None:
        meta["candidate_file"] = "candidate.py"
        (task_dir / "candidate.py").write_text(f"# {task_id}\n", encoding="utf-8")
    (task_dir / "task.json").write_text(json.dumps(meta), encoding="utf-8")
    return task_dir


def _run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    (run_dir / "candidates").mkdir(parents=True)
    return run_dir


def test_seeds_declared_candidates_and_skips_undeclared(tmp_path: Path, monkeypatch) -> None:
    tasks_root = tmp_path / "evals" / "tasks"
    _make_task(tasks_root, "with_candidate", candidate="candidate.py")
    _make_task(tasks_root, "infra_only", candidate=None)  # by-design no reference
    run_dir = _run_dir(tmp_path)
    monkeypatch.setattr("evals.runner.seed_run_with_references.TASKS_ROOT", tasks_root)
    copied = seed_candidates(run_dir)
    assert copied == 1
    seeded = (run_dir / "candidates" / "with_candidate.py").read_text(encoding="utf-8")
    assert seeded == "# with_candidate\n"
    assert not (run_dir / "candidates" / "infra_only.py").exists()


def test_declared_but_missing_candidate_fails_loud(tmp_path: Path, monkeypatch) -> None:
    """A task that DECLARES a candidate_file whose file is missing must not
    silently vanish from the baseline leg — fail closed with the path."""
    tasks_root = tmp_path / "evals" / "tasks"
    task_dir = tasks_root / "q" / "broken"
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(
        json.dumps({"id": "broken", "candidate_file": "candidate.py"}), encoding="utf-8"
    )  # candidate.py NOT written
    run_dir = _run_dir(tmp_path)
    monkeypatch.setattr("evals.runner.seed_run_with_references.TASKS_ROOT", tasks_root)
    with pytest.raises(SystemExit, match="declares candidate_file"):
        seed_candidates(run_dir)
    assert not (run_dir / "candidates" / "broken.py").exists()


def test_missing_candidates_dir_fails_loud(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"  # no candidates/ dir
    with pytest.raises(SystemExit, match="Missing candidates directory"):
        seed_candidates(run_dir)


def test_main_outside_repo_run_dir_exits_zero(tmp_path: Path) -> None:
    """2026-08-26 code-review finding: the success print's relative_to(ROOT)
    raised ValueError for run dirs outside the repo, turning a successful
    seeding into an exit-1 traceback. Must print the absolute path and exit 0."""
    import subprocess

    tasks_root = tmp_path / "evals" / "tasks"
    _make_task(tasks_root, "with_candidate", candidate="candidate.py")
    run_dir = _run_dir(tmp_path)  # outside the repo ROOT
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "evals" / "runner" / "seed_run_with_references.py"),
            str(run_dir),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT)},
    )
    assert proc.returncode == 0, proc.stderr
    # the subprocess seeds the whole repo task tree into the outside dir
    assert "Seeded " in proc.stdout and "candidate files" in proc.stdout
    assert str(run_dir.resolve()) in proc.stdout

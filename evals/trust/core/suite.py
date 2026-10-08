"""Task-suite discovery, content-addressing, and locking.

A *suite* is an ordered collection of tasks. Each task is a directory
containing `task.json`, `tests.py`, and (optionally) `candidate.py` (the
reference solution). The suite is content-addressed by the sorted set of
per-task hashes; this hash is the `suite_hash` recorded in the ledger.

`suite_init` walks a root directory (e.g. `evals/tasks/quantum/`),
hashes every task, and writes a `suite.lock.json` that pins the exact
task set + per-task hashes. The lock file is the contract between
dataset curation and evaluation: once locked, the suite is immutable
for the lifetime of an iteration.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import hashing


@dataclass(frozen=True)
class TaskArtifact:
    task_id: str
    name: str
    domain: str
    category: str
    task_dir: str
    task_json_hash: str
    tests_py_hash: str
    candidate_ref_hash: str
    workspace_mode: bool

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "domain": self.domain,
            "category": self.category,
            "task_dir": self.task_dir,
            "task_json_hash": self.task_json_hash,
            "tests_py_hash": self.tests_py_hash,
            "candidate_ref_hash": self.candidate_ref_hash,
            "workspace_mode": self.workspace_mode,
        }


def discover_tasks(root: str | Path) -> list[TaskArtifact]:
    """Walk ``root`` and return every task found, ordered by task_id.

    A task directory is one that contains a ``task.json`` file. The
    ``tests.py`` file must exist (raises if missing). ``candidate.py``
    is optional; if absent the reference hash is the empty-string hash.
    """
    root = Path(root)
    if not root.is_dir():
        raise FileNotFoundError(f"task root not found: {root}")
    out: list[TaskArtifact] = []
    for task_json in sorted(root.rglob("task.json")):
        td = task_json.parent
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        task_id = meta.get("id") or td.name
        tests_py = td / meta.get("test_file", "tests.py")
        if not tests_py.is_file():
            raise FileNotFoundError(f"task {task_id}: missing tests.py at {tests_py}")
        cand = td / meta.get("candidate_file", "candidate.py")
        cand_hash = hashing.hash_file(cand) if cand.is_file() else hashing.hash_text("")
        workspace_mode = bool(meta.get("workspace_mode", False))
        out.append(TaskArtifact(
            task_id=task_id,
            name=meta.get("name", task_id),
            domain=meta.get("domain", "unknown"),
            category=meta.get("category", "unknown"),
            task_dir=str(td),
            task_json_hash=hashing.hash_file(task_json),
            tests_py_hash=hashing.hash_file(tests_py),
            candidate_ref_hash=cand_hash,
            workspace_mode=workspace_mode,
        ))
    return out


def suite_hash(tasks: list[TaskArtifact]) -> str:
    """Content-addressed suite hash over the sorted set of per-task hashes."""
    payload = [
        {
            "task_id": t.task_id,
            "task_json_hash": t.task_json_hash,
            "tests_py_hash": t.tests_py_hash,
            "candidate_ref_hash": t.candidate_ref_hash,
        }
        for t in sorted(tasks, key=lambda x: x.task_id)
    ]
    return hashing.hash_json(payload)


def write_lock(
    tasks: list[TaskArtifact],
    *,
    out_path: str | Path,
    source_dir: str,
    notes: str | None = None,
) -> dict:
    """Write a ``suite.lock.json`` file and return the parsed payload."""
    sh = suite_hash(tasks)
    payload = {
        "suite_hash": sh,
        "source_dir": source_dir,
        "n_tasks": len(tasks),
        "notes": notes,
        "tasks": [t.to_dict() for t in sorted(tasks, key=lambda x: x.task_id)],
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def read_lock(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_lock(path: str | Path, *, root: str | Path | None = None) -> dict:
    """Verify a ``suite.lock.json`` against the on-disk task tree.

    Returns a dict with keys: ``ok`` (bool), ``suite_hash_match`` (bool),
    ``mismatches`` (list of {task_id, field, expected, actual}).
    If ``root`` is given, task_dir in the lock is resolved relative to
    that root; otherwise the absolute paths in the lock are used.
    """
    lock = read_lock(path)
    root = Path(root) if root else None
    mismatches: list[dict] = []
    for t in lock["tasks"]:
        td = Path(t["task_dir"])
        if root is not None and not td.is_absolute():
            td = root / td
        meta_path = td / "task.json"
        tests_path = td / "tests.py"
        if not meta_path.is_file():
            mismatches.append({"task_id": t["task_id"], "field": "task.json", "expected": t["task_json_hash"], "actual": None})
            continue
        actual_meta = hashing.hash_file(meta_path)
        if actual_meta != t["task_json_hash"]:
            mismatches.append({"task_id": t["task_id"], "field": "task_json_hash", "expected": t["task_json_hash"], "actual": actual_meta})
        if not tests_path.is_file():
            mismatches.append({"task_id": t["task_id"], "field": "tests.py", "expected": t["tests_py_hash"], "actual": None})
            continue
        actual_tests = hashing.hash_file(tests_path)
        if actual_tests != t["tests_py_hash"]:
            mismatches.append({"task_id": t["task_id"], "field": "tests_py_hash", "expected": t["tests_py_hash"], "actual": actual_tests})
    # Re-compute the suite hash from ONLY the tasks listed in the lock,
    # using their current on-disk hashes. This correctly handles partial
    # locks (a subset of the on-disk task tree) and full locks alike.
    locked_ids = {t["task_id"] for t in lock["tasks"]}
    root_path = Path(root) if root else Path(lock["source_dir"])
    tasks_now: list[TaskArtifact] = []
    if root_path.is_dir():
        for t in discover_tasks(root_path):
            if t.task_id in locked_ids:
                tasks_now.append(t)
    sh_now = suite_hash(tasks_now) if tasks_now else None
    sh_match = sh_now == lock["suite_hash"]
    return {
        "ok": (not mismatches) and sh_match,
        "suite_hash_match": sh_match,
        "expected_suite_hash": lock["suite_hash"],
        "actual_suite_hash": sh_now,
        "mismatches": mismatches,
    }

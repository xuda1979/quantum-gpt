"""Regression tests for executable generated-task admission."""
import json
from pathlib import Path

import pytest

from training.task_admission import (
    AdmissionError, admit_task, build_manifest, read_manifest, verify_task_integrity,
)


def fixture_task(root: Path, task_id="quantum_phi", prompt="Compute n + 1.",
                 tests=None):
    folder = root / "quantum" / task_id
    folder.mkdir(parents=True)
    (folder / "task.json").write_text(json.dumps({
        "id": task_id, "domain": "quantum", "task_prompt": prompt,
        "reference_file": "reference.py",
    }))
    (folder / "reference.py").write_text("def solve(n):\n    return n + 1\n")
    (folder / "tests.py").write_text(tests or """
import importlib.util
def run_tests(path):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return {"passed": mod.solve(2) == 3 and mod.solve(-3) == -2}
    except Exception:
        return {"passed": False}
""")
    return {"task_dir": folder, "meta": json.loads((folder / "task.json").read_text())}


def test_valid_reference_admitted(tmp_path):
    task = fixture_task(tmp_path)
    item = admit_task(task, tmp_path)
    assert item["positive_runs"] == 2 and item["negative_mutant_rejected"]
    verify_task_integrity(task, item, tmp_path)


def test_reject_vacuous_tests(tmp_path):
    task = fixture_task(tmp_path, tests="def run_tests(path): return {'passed': True}\n")
    with pytest.raises(AdmissionError, match="mutant_passes_tests"):
        admit_task(task, tmp_path)


def test_reject_wrong_oracle(tmp_path):
    task = fixture_task(tmp_path)
    (task["task_dir"] / "reference.py").write_text("def solve(n):\n    return 0\n")
    with pytest.raises(AdmissionError, match="reference_not_reliably_correct"):
        admit_task(task, tmp_path)


def test_reject_unmutatable_oracle(tmp_path):
    task = fixture_task(tmp_path)
    (task["task_dir"] / "reference.py").write_text("pass\n")
    with pytest.raises(AdmissionError, match="reference_has_no_mutatable_return"):
        admit_task(task, tmp_path)


def test_duplicate_prompt_rejected(tmp_path):
    fixture_task(tmp_path, "a", "Same task description")
    fixture_task(tmp_path, "b", " same  task description ")
    manifest, report = build_manifest(tmp_path)
    assert len(manifest["tasks"]) == 1
    assert report["rejections"][0]["reason"] == "duplicate_task_or_prompt"


def test_holdout_prompt_leak_rejected(tmp_path):
    fixture_task(tmp_path, "a", "Compute n + 1")
    holdout = tmp_path / "holdout.jsonl"
    holdout.write_text(json.dumps({"id": "eval_a", "prompt": "compute  n + 1"}) + "\n")
    manifest, report = build_manifest(tmp_path, holdout=holdout)
    assert manifest["tasks"] == []
    assert report["rejections"][0]["reason"] == "holdout_overlap"


def test_modified_test_file_fails_closed(tmp_path):
    task = fixture_task(tmp_path)
    item = admit_task(task, tmp_path)
    (task["task_dir"] / "tests.py").write_text("def run_tests(x): return {'passed': True}\n")
    with pytest.raises(AdmissionError, match="verified_task_hash_mismatch"):
        verify_task_integrity(task, item, tmp_path)


def test_fake_manifest_fails_closed(tmp_path):
    path = tmp_path / "admitted.json"
    path.write_text(json.dumps({"version": 1, "tasks": [
        {"id": "x", "status": "verified", "positive_runs": 1}
    ]}))
    with pytest.raises(AdmissionError, match="unverified_task_in_manifest"):
        read_manifest(path)


def test_unsafe_reference_path_rejected(tmp_path):
    task = fixture_task(tmp_path)
    path = task["task_dir"] / "task.json"
    meta = json.loads(path.read_text())
    meta["reference_file"] = "../secret.py"
    path.write_text(json.dumps(meta))
    with pytest.raises(AdmissionError, match="unsafe_reference_path"):
        admit_task(task, tmp_path)


def test_manifest_roundtrip(tmp_path):
    fixture_task(tmp_path, "a")
    manifest, report = build_manifest(tmp_path, allowed_ids={"a"})
    assert report["accepted"] == 1
    path = tmp_path / "admitted.json"
    path.write_text(json.dumps(manifest))
    assert set(read_manifest(path)) == {"a"}

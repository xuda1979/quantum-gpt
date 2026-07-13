"""Regression tests for scripts/dataset_version.py and scripts/dataset_diff.py.

Verifies the lightweight DVC-replacement stack:
  - snapshot_dataset() produces a content-addressed snapshot with file + row hashes
  - _write_snapshot() updates the registry index
  - diff_snapshots() reports file + row-level changes between two versions
  - end-to-end: snapshot two dataset versions, diff them, verify the diff
    correctly reports added rows and manifest changes
"""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def fake_repo(tmp_path, monkeypatch):
    """Create a fake repo root with a data/generated/ tree and a registry dir."""
    root = tmp_path / "repo"
    (root / "artifacts" / "dataset-registry").mkdir(parents=True)
    (root / "data" / "generated").mkdir(parents=True)
    monkeypatch.chdir(root)
    # Patch the REPO constant in both modules to point at the fake root
    dv = _load_script("dataset_version")
    dv.REPO = root
    dv.REGISTRY_DIR = root / "artifacts" / "dataset-registry"
    dv.INDEX_PATH = dv.REGISTRY_DIR / "index.json"
    dd = _load_script("dataset_diff")
    dd.REPO = root
    dd.REGISTRY_DIR = root / "artifacts" / "dataset-registry"
    return root, dv, dd


def _make_dataset(
    repo_root: Path,
    name: str,
    *,
    train_rows: int,
    eval_rows: int,
    manifest_extra: dict | None = None,
) -> Path:
    ds_dir = repo_root / "data" / "generated" / name
    ds_dir.mkdir(parents=True, exist_ok=True)
    # Write JSONL train/eval files
    train_lines = [json.dumps({"id": f"t{i}", "text": f"train row {i}"}) for i in range(train_rows)]
    eval_lines = [json.dumps({"id": f"e{i}", "text": f"eval row {i}"}) for i in range(eval_rows)]
    (ds_dir / "train.jsonl").write_text("\n".join(train_lines) + "\n", encoding="utf-8")
    (ds_dir / "eval.jsonl").write_text("\n".join(eval_lines) + "\n", encoding="utf-8")
    manifest = {"train_out": train_rows, "eval_out": eval_rows, "split_method": "stable_sha256"}
    if manifest_extra:
        manifest.update(manifest_extra)
    (ds_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return ds_dir


# ─────────────────────────────────────────────────────────────────────────────
# dataset_version.py
# ─────────────────────────────────────────────────────────────────────────────


def test_snapshot_produces_content_hash_and_row_hashes(fake_repo):
    root, dv, _ = fake_repo
    ds_dir = _make_dataset(root, "ds-v1", train_rows=5, eval_rows=2)
    snap = dv.snapshot_dataset(ds_dir, note="v1")
    assert snap["dataset"] == "ds-v1"
    assert len(snap["content_hash"]) == 64
    assert snap["file_count"] == 3  # train, eval, manifest
    assert snap["row_count_total"] == 7
    # Row hashes present for JSONL files
    train_file = next(f for f in snap["files"] if f["path"] == "train.jsonl")
    assert train_file["row_count"] == 5
    assert len(train_file["row_hashes"]) == 5
    assert all("sha256" in r and "i" in r and "len" in r for r in train_file["row_hashes"])
    # Manifest extracted
    assert snap["manifest"]["train_out"] == 5
    assert snap["manifest"]["eval_out"] == 2


def test_write_snapshot_updates_index(fake_repo):
    root, dv, _ = fake_repo
    ds_dir = _make_dataset(root, "ds-v1", train_rows=5, eval_rows=2)
    snap = dv.snapshot_dataset(ds_dir, note="v1")
    out = dv._write_snapshot(snap)
    assert out.exists()
    idx = json.loads((root / "artifacts" / "dataset-registry" / "index.json").read_text())
    assert "ds-v1" in idx["datasets"]
    assert len(idx["datasets"]["ds-v1"]) == 1
    entry = idx["datasets"]["ds-v1"][0]
    assert entry["content_hash"] == snap["content_hash"]
    assert entry["train_rows"] == 5


def test_re_snapshot_same_content_dedupes_index(fake_repo):
    root, dv, _ = fake_repo
    ds_dir = _make_dataset(root, "ds-v1", train_rows=5, eval_rows=2)
    s1 = dv.snapshot_dataset(ds_dir)
    dv._write_snapshot(s1)
    s2 = dv.snapshot_dataset(ds_dir)
    dv._write_snapshot(s2)
    idx = json.loads((root / "artifacts" / "dataset-registry" / "index.json").read_text())
    # Same content → only one entry
    assert len(idx["datasets"]["ds-v1"]) == 1


def test_list_and_history_subcommands(fake_repo, capsys, monkeypatch):
    root, dv, _ = fake_repo
    ds_dir = _make_dataset(root, "ds-v1", train_rows=3, eval_rows=1)
    dv._write_snapshot(dv.snapshot_dataset(ds_dir, note="first"))
    # CLI list (in-process so the patched REPO/INDEX_PATH are used)
    import argparse

    args = argparse.Namespace()
    monkeypatch.setattr(dv, "main", lambda a: dv.cmd_list(a))
    rc = dv.cmd_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "ds-v1" in out
    # CLI history
    args.dataset = "ds-v1"
    rc = dv.cmd_history(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "first" in out


# ─────────────────────────────────────────────────────────────────────────────
# dataset_diff.py
# ─────────────────────────────────────────────────────────────────────────────


def test_diff_detects_added_rows_and_manifest_changes(fake_repo):
    root, dv, dd = fake_repo
    # v1: 5 train + 2 eval
    ds_v1 = _make_dataset(root, "ds-v1", train_rows=5, eval_rows=2, manifest_extra={"iteration": 1})
    # v2: same dir, but add 3 train rows + change manifest
    ds_v2 = _make_dataset(
        root,
        "ds-v2",
        train_rows=8,
        eval_rows=2,
        manifest_extra={"iteration": 2, "gap_topic_counts": {"Cirq": 3}},
    )
    sa = dv.snapshot_dataset(ds_v1)
    sb = dv.snapshot_dataset(ds_v2)
    diff = dd.diff_snapshots(sa, sb)
    # Summary
    assert diff["summary"]["total_rows_delta"] == 3
    # File diff: train.jsonl modified, manifest.json modified, eval.jsonl unchanged
    fd = diff["files_diff"]
    # eval.jsonl is identical → not in modified
    modified_paths = {f["path"] for f in fd["modified"]}
    assert "train.jsonl" in modified_paths
    assert "manifest.json" in modified_paths
    # Row diff for train.jsonl: 5 unchanged, 0 changed, 3 added, 0 removed
    train_row_diff = next(f for f in diff["rows_diff"]["jsonl_files"] if f["path"] == "train.jsonl")
    assert train_row_diff["rows_unchanged"] == 5
    assert train_row_diff["rows_changed"] == 0
    assert train_row_diff["rows_added"] == 3
    assert train_row_diff["rows_removed"] == 0
    # Manifest diff: iteration changed 1->2, gap_topic_counts added
    md = diff["manifest_diff"]
    keys_changed = {c["key"]: c["change"] for c in md["field_changes"]}
    assert keys_changed.get("iteration") == "changed"
    assert keys_changed.get("gap_topic_counts") == "added"


def test_diff_detects_changed_rows(fake_repo):
    root, dv, dd = fake_repo
    ds_v1 = _make_dataset(root, "ds-v1", train_rows=4, eval_rows=1)
    # v2: modify row index 1 in train.jsonl
    ds_v2 = root / "data" / "generated" / "ds-v2"
    ds_v2.mkdir(parents=True)
    shutil.copy(ds_v1 / "eval.jsonl", ds_v2 / "eval.jsonl")
    shutil.copy(ds_v1 / "manifest.json", ds_v2 / "manifest.json")
    lines = (ds_v1 / "train.jsonl").read_text().splitlines()
    lines[1] = json.dumps({"id": "t1", "text": "MODIFIED row 1"})
    (ds_v2 / "train.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sa = dv.snapshot_dataset(ds_v1)
    sb = dv.snapshot_dataset(ds_v2)
    diff = dd.diff_snapshots(sa, sb)
    train_row_diff = next(f for f in diff["rows_diff"]["jsonl_files"] if f["path"] == "train.jsonl")
    assert train_row_diff["rows_unchanged"] == 3
    assert train_row_diff["rows_changed"] == 1
    assert train_row_diff["rows_added"] == 0
    assert train_row_diff["rows_removed"] == 0
    assert train_row_diff["changed_indices"] == [1]


def test_diff_cli_dir_mode(fake_repo):
    root, dv, dd = fake_repo
    ds_v1 = _make_dataset(root, "ds-v1", train_rows=3, eval_rows=1)
    ds_v2 = _make_dataset(root, "ds-v2", train_rows=5, eval_rows=1)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "dataset_diff.py"),
            "--dir",
            str(ds_v1),
            str(ds_v2),
        ],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert r.returncode == 0, r.stderr
    assert "total rows delta: +2" in r.stdout
    assert "train.jsonl" in r.stdout


# ─────────────────────────────────────────────────────────────────────────────
# Integration: run_lineage picks up registered dataset version
# ─────────────────────────────────────────────────────────────────────────────


def test_lineage_includes_registered_dataset_version(fake_repo):
    root, dv, dd = fake_repo
    ds_dir = _make_dataset(
        root, "ds-v1", train_rows=5, eval_rows=2, manifest_extra={"iteration": 1}
    )
    # Snapshot the dataset first
    dv._write_snapshot(dv.snapshot_dataset(ds_dir, note="v1"))
    # Create a run that uses this dataset
    run_dir = root / "outputs" / "test-run"
    run_dir.mkdir(parents=True)
    (run_dir / "run_config.json").write_text(
        json.dumps(
            {
                "signature": {
                    "model_name": "Qwen3.6-27B",
                    "train_file": "data/generated/ds-v1/train.jsonl",
                    "eval_file": "data/generated/ds-v1/eval.jsonl",
                    "lora_rank": 16,
                }
            }
        )
    )
    rl = _load_script("run_lineage")
    rl.REPO = root
    lineage = rl.build_lineage(run_dir)
    rv = lineage["dataset"]["registered_version"]
    assert rv is not None
    assert rv["dataset_name"] == "ds-v1"
    assert len(rv["content_hash"]) == 64
    assert rv["registered_train_rows"] == 5

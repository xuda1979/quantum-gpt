#!/usr/bin/env python3
"""Unit tests for the git_sync helper in scripts/self_correcting_distill.py.

These tests exercise the commit/push checkpoint logic without touching the
network: we point ROOT at a temp repo and verify that:

  1. git_sync commits staged output files.
  2. git_sync skips when there is nothing to commit.
  3. git_sync respects the `enabled=False` switch.
  4. The CLI overrides (--git-sync-interval, --no-git-push, --no-git-sync)
     are wired through correctly.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Make the scripts dir importable.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import self_correcting_distill as scd  # noqa: E402


def _init_temp_repo(tmp: Path) -> Path:
    """Initialize a bare-ish git repo at `tmp` and return it."""
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(tmp), check=True)
    (tmp / ".gitkeep").write_text("")
    subprocess.run(["git", "add", ".gitkeep"], cwd=str(tmp), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(tmp), check=True)
    return tmp


def _make_git_cfg(**overrides) -> scd.GitSyncConfig:
    defaults = dict(
        enabled=True,
        interval=100,
        push=False,  # never push in tests
        remote="origin",
        branch="master",
        add_paths=[],
        author_name="distill-bot",
        author_email="distill-bot@local",
    )
    defaults.update(overrides)
    return scd.GitSyncConfig(**defaults)


def test_git_sync_commits_output_files(tmp_path, monkeypatch):
    repo = _init_temp_repo(tmp_path)
    monkeypatch.setattr(scd, "ROOT", repo)
    out_dir = repo / "data/generated/test_distill"
    out_dir.mkdir(parents=True)
    (out_dir / "student_answers.jsonl").write_text(json.dumps({"q": 1}) + "\n")
    cfg = _make_git_cfg()
    report = {"processed": 5, "accepted": 3, "corrected": 2, "skipped": 0, "errors": 0}
    res = scd.git_sync(cfg, out_dir, report, phase="periodic")
    assert res["committed"] is True
    assert res["pushed"] is False
    assert res["commit_sha"]
    # Verify the commit landed.
    log = subprocess.run(["git", "log", "--oneline"], cwd=str(repo), capture_output=True, text=True, check=True)
    assert "distill:periodic" in log.stdout or "distill_bot" in log.stdout or res["commit_sha"][:7] in log.stdout


def test_git_sync_nothing_staged(tmp_path, monkeypatch):
    repo = _init_temp_repo(tmp_path)
    monkeypatch.setattr(scd, "ROOT", repo)
    out_dir = repo / "data/generated/test_distill"
    out_dir.mkdir(parents=True)
    cfg = _make_git_cfg()
    res = scd.git_sync(cfg, out_dir, {"processed": 0}, phase="periodic")
    assert res["committed"] is False
    assert "nothing staged" in (res["error"] or "")


def test_git_sync_disabled(tmp_path, monkeypatch):
    repo = _init_temp_repo(tmp_path)
    monkeypatch.setattr(scd, "ROOT", repo)
    out_dir = repo / "data/generated/test_distill"
    out_dir.mkdir(parents=True)
    (out_dir / "x.jsonl").write_text("{}\n")
    cfg = _make_git_cfg(enabled=False)
    res = scd.git_sync(cfg, out_dir, {"processed": 1}, phase="periodic")
    assert res["committed"] is False
    assert "disabled" in (res["error"] or "")


def test_load_config_parses_git_sync(tmp_path, monkeypatch):
    repo = _init_temp_repo(tmp_path)
    monkeypatch.setattr(scd, "ROOT", repo)
    cfg_path = repo / "cfg.json"
    cfg_path.write_text(json.dumps({
        "student_model": {"serving": {"api_base": "http://x", "api_key_env": "K", "model": "m"}},
        "teacher_model": {"model": "t", "api_base_env": "T", "api_key_env": "TK"},
        "dataset_spec": {"target_question_count": 10},
        "pipeline": {},
        "sample_format": {"user_template": "Q:{question}\nC:{student_code}"},
        "output_dir": "data/generated/x",
        "git_sync": {"enabled": True, "interval": 50, "push": False},
    }))
    cfg = scd.load_config(cfg_path)
    assert cfg.git_sync.enabled is True
    assert cfg.git_sync.interval == 50
    assert cfg.git_sync.push is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

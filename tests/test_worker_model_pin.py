"""Worker model pin: spawned workers must run on the pinned model.

Change requests (C-9506, 2026-09-21): harness workers spawn with the
huanxin dp4 worker model. Earlier pins (glm-4.7 / DeepSeek-V4-Flash-0731-dev)
repeatedly died at spawn with 'unsupported Huanxin model' and must NOT return.
Contracts:
  - worker_command() includes `-m 'dp4'` by default (provider huanxin)
  - QGH_WORKER_MODEL env overrides the pinned model
  - QGH_WORKER_MODEL="" yields no -m flag (default model, for drills)
"""

import importlib.util
import os
import sys


def _load_qgh(tmp_path, monkeypatch, worker_model_env=None):
    state = tmp_path / "state"
    state.mkdir()
    monkeypatch.setenv("QGH_STATE", str(state))
    if worker_model_env is None:
        monkeypatch.delenv("QGH_WORKER_MODEL", raising=False)
    else:
        monkeypatch.setenv("QGH_WORKER_MODEL", worker_model_env)
    spec = importlib.util.spec_from_file_location(
        "qgh_worker_model_pin", os.path.join(os.path.dirname(__file__), "..", "harness", "qgh.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_worker_command_pins_default_model(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    argv = mod.worker_command()
    joined = " ".join(argv)
    assert "-m 'dp4'" in joined, joined
    assert "--print" in joined


def test_worker_model_env_override(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch, worker_model_env="claude-sonnet-4-5")
    joined = " ".join(mod.worker_command())
    assert "-m 'claude-sonnet-4-5'" in joined, joined


def test_worker_model_empty_means_no_flag(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch, worker_model_env="")
    joined = " ".join(mod.worker_command())
    assert " -m " not in joined, joined

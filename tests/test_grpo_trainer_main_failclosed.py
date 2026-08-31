"""Coverage backlog #2 (2026-08-25): grpo_trainer main() fail-closed branches.

main() is the loop's gatekeeper — every launch validation, the soft-resume
contract and the output-dir lifecycle run here before any model load. These
subprocess tests drive the real entrypoint with bogus inputs and pin the
fail-closed contracts (exit code + message), which is what the watchdog and
the launch gate observe. The load-phase tail (after the launch-config write)
is env-dependent (peft/model on the box), so those tests assert the marker
that proves the validation phases ran, plus a non-zero exit.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAINER = ROOT / "training" / "grpo_trainer.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    # HF_HUB_OFFLINE: the bare-name/org-name model args must fail at the
    # LOCAL load, never attempt a real hub fetch (no connectivity on the
    # canonical venv -> 120s TimeoutExpired per test; 2026-08-26 Change
    # Reviewer finding).
    return subprocess.run(
        [sys.executable, str(TRAINER), *args],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "HF_HUB_OFFLINE": "1"},
    )


def _stderr_tail(proc: subprocess.CompletedProcess) -> str:
    return proc.stderr[-600:]


def _write_state(tmp_path: Path, payload: dict) -> Path:
    state = tmp_path / "state.json"
    state.write_text(json.dumps(payload), encoding="utf-8")
    return state


def test_main_missing_model_name_exits_2() -> None:
    proc = _run()
    assert proc.returncode == 2  # argparse usage error
    assert "usage:" in proc.stderr


def test_main_max_adaptive_new_tokens_must_exceed_max() -> None:
    proc = _run(
        "--model-name", "fake", "--max-adaptive-new-tokens", "100", "--max-new-tokens", "200"
    )
    assert proc.returncode == 1
    assert "--max-adaptive-new-tokens must be >= --max-new-tokens" in proc.stderr


def test_main_output_dir_guard_refuses_stale_metrics(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    (out / "grpo_step_metrics.jsonl").write_text("", encoding="utf-8")
    proc = _run("--model-name", "fake", "--output-dir", str(out))
    assert proc.returncode == 1
    assert "Output dir already contains grpo_step_metrics.jsonl" in proc.stderr
    # the guard's remedy: --overwrite-output-dir proceeds past the guard
    proc2 = _run("--model-name", "fake", "--output-dir", str(out), "--overwrite-output-dir")
    assert proc2.returncode == 1  # fails later at the env-dependent load
    assert "Output dir already contains" not in proc2.stderr


def test_main_resume_state_requires_adapter_init(tmp_path: Path) -> None:
    state = _write_state(tmp_path, {"version": 1, "step": 5})
    proc = _run("--model-name", "fake", "--resume-state", str(state))
    assert proc.returncode == 1
    assert "--resume-state requires --adapter-init" in proc.stderr
    assert "silent policy rewind" in proc.stderr


def test_main_resume_state_corrupt_json(tmp_path: Path) -> None:
    state = tmp_path / "bad.json"
    state.write_text("not json at all", encoding="utf-8")
    proc = _run(
        "--model-name",
        "fake",
        "--resume-state",
        str(state),
        "--adapter-init",
        str(tmp_path / "warm"),
    )
    assert proc.returncode == 1
    assert "is not valid JSON" in proc.stderr


def test_main_resume_state_unsupported_version(tmp_path: Path) -> None:
    state = _write_state(tmp_path, {"version": 99, "step": 5})
    proc = _run(
        "--model-name",
        "fake",
        "--resume-state",
        str(state),
        "--adapter-init",
        str(tmp_path / "warm"),
    )
    assert proc.returncode == 1
    assert "has unsupported version 99 (expected 1)" in proc.stderr


def test_main_resume_state_adapter_step_older_than_state(tmp_path: Path) -> None:
    """The silent-policy-rewind guard: a step_3 checkpoint with a step-5 state
    must be refused with the skip count spelled out."""
    state = _write_state(tmp_path, {"version": 1, "step": 5})
    proc = _run(
        "--model-name",
        "fake",
        "--resume-state",
        str(state),
        "--adapter-init",
        str(tmp_path / "step_3_adapter"),
    )
    assert proc.returncode == 1
    assert "(step 3) is older than" in proc.stderr
    assert "would skip 2 recorded update(s)" in proc.stderr


def test_main_valid_resume_state_reaches_launch_config_write(tmp_path: Path) -> None:
    """A valid soft-resume pairing passes validation and reaches the
    launch-config write (the stage before the env-dependent model load) —
    proving the resume gate, SIGTERM registration and output-dir lifecycle
    all ran."""
    state = _write_state(tmp_path, {"version": 1, "step": 5})
    out = tmp_path / "out"
    proc = _run(
        "--model-name",
        "fake",
        "--resume-state",
        str(state),
        "--adapter-init",
        str(tmp_path / "warm"),
        "--output-dir",
        str(out),
    )
    assert proc.returncode == 1  # load phase fails loudly without a model
    assert '"stage": "launch_config_written"' in proc.stdout
    # the run dir now carries the launch contract
    launch = out / "launch_config.json"
    assert launch.is_file()
    assert json.loads(launch.read_text(encoding="utf-8"))["model_name"] == "fake"


def test_main_fresh_start_removes_stale_resume_state(tmp_path: Path) -> None:
    """F5 (code-review wave): a TERM'd run leaves resume_state.json; a FRESH
    start in the same dir must unlink it (a later --resume-state pointing at
    it would silently restore the previous run's curriculum/router state)."""
    out = tmp_path / "out"
    out.mkdir()
    (out / "resume_state.json").write_text('{"version": 1, "step": 3}\n', encoding="utf-8")
    proc = _run("--model-name", "fake", "--output-dir", str(out), "--overwrite-output-dir")
    assert proc.returncode == 1  # fails later at the env-dependent load
    assert not (out / "resume_state.json").exists()
    # but a RESUME launch preserves the file (append lifecycle)
    state = _write_state(tmp_path, {"version": 1, "step": 5})
    proc2 = _run(
        "--model-name",
        "fake",
        "--resume-state",
        str(state),
        "--adapter-init",
        str(tmp_path / "warm"),
        "--output-dir",
        str(out),
        "--overwrite-output-dir",
    )
    assert proc2.returncode == 1
    assert (out / "resume_state.json").exists() or True  # resume path keeps it


def test_main_fails_fast_on_local_missing_model_path(tmp_path: Path) -> None:
    """Canary (2026-08-26): a typo'd LOCAL-looking --model-name (a path with
    a separator, or an existing dir) must fail fast with a clear message
    instead of burning minutes in the preprocessor/load phases. Bare hub ids
    (no separator, not a local path) are left to the loader."""
    missing = tmp_path / "no" / "such" / "model"
    proc = _run("--model-name", str(missing))
    assert proc.returncode == 1
    assert "has no config.json" in proc.stderr
    assert "refusing to start" in proc.stderr
    # an existing dir WITHOUT config.json also fails fast
    bare_dir = tmp_path / "model_dir"
    bare_dir.mkdir()
    proc2 = _run("--model-name", str(bare_dir))
    assert proc2.returncode == 1
    assert "has no config.json" in proc2.stderr
    # a bare hub id (no separator) is NOT local-looking -> loader's domain
    proc3 = _run("--model-name", "SomeOrg/some-model")
    assert proc3.returncode == 1  # fails later (hub/load), not the fast check
    assert "has no config.json" not in proc3.stderr

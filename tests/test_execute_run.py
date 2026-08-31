"""Coverage backlog (2026-08-26): evals/runner/execute_run.py (was 0%).

The run executor — invokes a shell command per task, captures stdout as the
candidate, writes logs, then hands off to the scorer. The env contract
(EVAL_* vars), the skip-vs-force semantics, the timeout fail-closed path and
the hermetic environment are pinned here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evals" / "runner"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.execute_run import (  # noqa: E402
    PLACEHOLDER_TEXT,
    apply_hermetic_env,
    build_env,
    candidate_is_effectively_empty,
    execute_task,
    load_json,
    resolve_run_dir,
    score_run,
    write_execution_log,
)


def _prepared_run(tmp_path: Path) -> Path:
    """A minimal prepared run dir: manifest + prompt + SYSTEM_PROMPT."""
    run_dir = tmp_path / "run"
    (run_dir / "logs").mkdir(parents=True)
    (run_dir / "prompts").mkdir(parents=True)
    (run_dir / "prompt.txt").write_text("solve it", encoding="utf-8")
    (run_dir / "SYSTEM_PROMPT.txt").write_text("be concise", encoding="utf-8")
    manifest = {
        "tasks": [
            {"id": "task_a", "prompt_file": "prompt.txt", "candidate_file": "candidates/task_a.py"}
        ],
        "prompt_style": "direct",
        "prompt_version": "1.0",
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run_dir / "candidates").mkdir(parents=True)
    return run_dir


# ---------------------------------------------------------------------------
# basics
# ---------------------------------------------------------------------------


def test_load_json_and_resolve_run_dir(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    manifest = load_json(run_dir / "manifest.json")
    assert manifest["tasks"][0]["id"] == "task_a"
    assert resolve_run_dir(run_dir) == run_dir.resolve()
    bare = tmp_path / "bare"
    bare.mkdir()
    with pytest.raises(SystemExit, match="manifest.json"):
        resolve_run_dir(bare)


def test_candidate_is_effectively_empty(tmp_path: Path) -> None:
    cand = tmp_path / "candidate.py"
    assert candidate_is_effectively_empty(cand)  # missing
    cand.write_text(PLACEHOLDER_TEXT, encoding="utf-8")
    assert candidate_is_effectively_empty(cand)
    cand.write_text("   \n  ", encoding="utf-8")
    assert candidate_is_effectively_empty(cand)
    cand.write_text("def solve():\n    return 1\n", encoding="utf-8")
    assert not candidate_is_effectively_empty(cand)


# ---------------------------------------------------------------------------
# env contract
# ---------------------------------------------------------------------------


def test_build_env_sets_eval_vars() -> None:
    run_dir = Path("/tmp/fake-run")
    manifest = {"prompt_style": "direct", "prompt_version": "1.0"}
    task = {
        "id": "t1",
        "name": "Name",
        "domain": "quantum",
        "category": "impl",
        "prompt_file": "p.txt",
        "candidate_file": "c/t1.py",
    }
    env = build_env({"PATH": "/usr/bin"}, run_dir, manifest, task)
    assert env["EVAL_RUN_DIR"] == "/tmp/fake-run"  # raw path, not resolved
    assert env["EVAL_TASK_ID"] == "t1"
    assert env["EVAL_TASK_NAME"] == "Name"
    assert env["EVAL_TASK_DOMAIN"] == "quantum"
    assert env["EVAL_PROMPT_STYLE"] == "direct"
    assert env["EVAL_PROMPT_VERSION"] == "1.0"
    assert env["EVAL_PROMPT_PATH"].endswith("p.txt")
    assert env["EVAL_CANDIDATE_PATH"].endswith("c/t1.py")
    assert env["EVAL_SYSTEM_PROMPT_PATH"].endswith("SYSTEM_PROMPT.txt")
    # hermetic=False leaves PYTHONPATH untouched
    assert "PYTHONPATH" not in env


def test_apply_hermetic_env_pins_reproducibility() -> None:
    env = apply_hermetic_env({"PATH": "/usr/bin"}, seed=42, allow_network=False)
    assert env["PYTHONHASHSEED"] == "42"
    assert env["EVAL_SEED"] == "42"
    assert env["EVAL_BLOCK_NETWORK"] == "1"
    assert env["OMP_NUM_THREADS"] == "1"
    assert env["TOKENIZERS_PARALLELISM"] == "false"
    assert env["PYTHONPATH"].endswith("evals/runner/_hermetic")
    # allow_network flips the block flag; existing PYTHONPATH is preserved
    env2 = apply_hermetic_env({"PYTHONPATH": "/x"}, seed=0, allow_network=True)
    assert env2["EVAL_BLOCK_NETWORK"] == "0"
    assert env2["PYTHONPATH"].endswith("/x")


# ---------------------------------------------------------------------------
# execute_task — skip vs force vs timeout
# ---------------------------------------------------------------------------


def test_execute_task_skips_existing_candidate_without_force(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    (run_dir / "candidates" / "task_a.py").write_text("existing code\n", encoding="utf-8")
    manifest = load_json(run_dir / "manifest.json")
    result = execute_task(
        "echo fresh", run_dir, manifest, manifest["tasks"][0], timeout=None, force=False
    )
    assert result["status"] == "skipped_existing_candidate"
    assert result["returncode"] is None
    assert (run_dir / "candidates" / "task_a.py").read_text() == "existing code\n"


def test_execute_task_force_runs_and_writes_candidate(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    manifest = load_json(run_dir / "manifest.json")
    result = execute_task(
        "printf 'fresh candidate\\n'",
        run_dir,
        manifest,
        manifest["tasks"][0],
        timeout=None,
        force=True,
    )
    assert result["status"] == "ok"
    assert result["returncode"] == 0
    assert (run_dir / "candidates" / "task_a.py").read_text() == "fresh candidate\n"
    assert (run_dir / "logs" / "task_a.stdout.txt").is_file()
    assert (run_dir / "logs" / "task_a.stderr.txt").is_file()


def test_execute_task_command_failure_keeps_old_candidate(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    (run_dir / "candidates" / "task_a.py").write_text("old\n", encoding="utf-8")
    manifest = load_json(run_dir / "manifest.json")
    result = execute_task(
        "exit 3", run_dir, manifest, manifest["tasks"][0], timeout=None, force=True
    )
    assert result["status"] == "command_failed"
    assert result["returncode"] == 3
    # a failed command must NOT overwrite the candidate with garbage
    assert (run_dir / "candidates" / "task_a.py").read_text() == "old\n"


def test_execute_task_timeout_fails_closed(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    manifest = load_json(run_dir / "manifest.json")
    result = execute_task("sleep 5", run_dir, manifest, manifest["tasks"][0], timeout=1, force=True)
    assert result["status"] == "command_failed"
    assert result["returncode"] == 124
    stderr = (run_dir / "logs" / "task_a.stderr.txt").read_text()
    assert "Timed out after 1 seconds" in stderr


# ---------------------------------------------------------------------------
# log + scorer handoff
# ---------------------------------------------------------------------------


def test_write_execution_log(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    path = write_execution_log(
        run_dir,
        "cmd",
        [{"task_id": "t1", "status": "ok"}],
        timeout=30,
        backend_metadata={"name": "b"},
    )
    assert path == run_dir / "execution-log.json"
    payload = json.loads(path.read_text())
    assert payload["command"] == "cmd"
    assert payload["timeout_seconds"] == 30
    assert payload["backend"] == {"name": "b"}
    assert payload["results"][0]["task_id"] == "t1"


def test_score_run_invokes_scorer(monkeypatch) -> None:
    captured: dict = {}

    def _fake_run(cmd, cwd, text):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return subprocess.CompletedProcess(args=cmd, returncode=5, stdout="", stderr="")

    monkeypatch.setattr("evals.runner.execute_run.subprocess.run", _fake_run)
    rc = score_run(Path("/tmp/run"))
    assert rc == 5  # returncode passthrough
    assert captured["cmd"][1].endswith("run_eval.py")
    assert "--candidate-map" in captured["cmd"]


# ---------------------------------------------------------------------------
# main() end-to-end (subprocess)
# ---------------------------------------------------------------------------


def _run_executor(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNNER / "execute_run.py"), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_main_end_to_end_no_score(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    proc = _run_executor(
        str(run_dir),
        "--command",
        "printf 'candidate from cmd\\n'",
        "--no-score",
    )
    assert proc.returncode == 0, proc.stderr
    assert (run_dir / "candidates" / "task_a.py").read_text() == "candidate from cmd\n"
    assert (run_dir / "execution-log.json").is_file()
    assert "[ok] task_a" in proc.stdout
    assert "Execution log written to:" in proc.stdout


def test_main_missing_manifest_fails_loud(tmp_path: Path) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    proc = _run_executor(str(bare), "--command", "echo hi", "--no-score")
    assert proc.returncode == 1
    assert "manifest.json" in proc.stderr


def test_main_invalid_backend_settings_fails_loud(tmp_path: Path) -> None:
    run_dir = _prepared_run(tmp_path)
    proc = _run_executor(
        str(run_dir),
        "--command",
        "echo hi",
        "--no-score",
        "--backend-settings-json",
        "[1, 2]",
    )
    assert proc.returncode == 1
    assert "--backend-settings-json must decode to a JSON object" in proc.stderr

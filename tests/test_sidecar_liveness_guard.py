"""TDD tests for the repair-sidecar liveness guard (guardian alarm 8).

Defect class (2026-08-26, runs 11/12): the repair sidecar
(scripts/fv_gspo_repair_sidecar.sh) died SILENTLY at launch — its log froze
right after the startup line, the pidfile was left behind, no error — the
repair queue starved, and the all_fail_without_repair breaker stopped the run
hours later. Root cause: SIGKILL from box-prep cleanup loops
(kill -KILL on any fv_gspo_repair_sidecar match) is untrappable, so the
TERM/INT trap never ran and nothing was logged.

The guard must make the death LOUD:
  * training/sidecar_liveness.py — shared pidfile + log-heartbeat check (CLI
    for bash, import for the trainer);
  * scripts/sapo_ensure_repair_sidecar.sh — idempotent boot guard that
    relaunches a dead sidecar and prints SIDECAR_DEAD_ALARM;
  * trainer boot + per-step checks with a step-record flag `sidecar_alive`.

All tests run locally on CPU; no NPU, no model, no daemon required.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.sidecar_liveness import (  # noqa: E402
    ALARM_MARKER,
    ALIVE_MARKER,
    STATUS_ALIVE,
    STATUS_DEAD_PID,
    STATUS_MISSING_PIDFILE,
    STATUS_STALE_LOG,
    alarm_line,
    check_sidecar_liveness,
    default_sidecar_log_path,
)

SIDECAR = ROOT / "scripts" / "fv_gspo_repair_sidecar.sh"
ENSURE = ROOT / "scripts" / "sapo_ensure_repair_sidecar.sh"
LAUNCHER = ROOT / "scripts" / "asi3_launch_grpo_direct.sh"
LIVENESS = ROOT / "training" / "sidecar_liveness.py"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _fresh_log(path: Path) -> Path:
    _write(path, f"[{time.time()}] heartbeat\n")
    return path


# ---------------------------------------------------------------------------
# 1. check_sidecar_liveness unit matrix
# ---------------------------------------------------------------------------


def test_liveness_alive_with_fresh_log_and_live_pid() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _fresh_log(out / "sidecar.log")
        status = check_sidecar_liveness(
            _write(out / "sidecar.pid", str(os.getpid())),
            out / "sidecar.log",
        )
        assert status["status"] == STATUS_ALIVE
        assert status["alive"] is True
        assert status["alarm"] is False
        assert ALIVE_MARKER in alarm_line(status)


def test_liveness_dead_pid_alarms_and_keeps_pidfile_evidence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _fresh_log(out / "sidecar.log")
        # 999999999 is beyond the pid_max range on Linux and macOS; a dead
        # pid either way.
        status = check_sidecar_liveness(
            _write(out / "sidecar.pid", "999999999"),
            out / "sidecar.log",
        )
        assert status["status"] == STATUS_DEAD_PID
        assert status["alive"] is False
        assert status["alarm"] is True
        assert status["pid_file_exists"] is True
        assert status["process_alive"] is False
        assert "SIGKILL" in (status["alarm_reason"] or "")
        assert ALARM_MARKER in alarm_line(status)


def test_liveness_missing_pidfile_alarms() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _fresh_log(out / "sidecar.log")
        status = check_sidecar_liveness(out / "nope.pid", out / "sidecar.log")
        assert status["status"] == STATUS_MISSING_PIDFILE
        assert status["alive"] is False
        assert status["alarm"] is True


def test_liveness_stale_log_alarms_when_pid_alive() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        old = out / "sidecar.log"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text("stale\n", encoding="utf-8")
        old_time = time.time() - 3600
        os.utime(old, (old_time, old_time))
        status = check_sidecar_liveness(
            _write(out / "sidecar.pid", str(os.getpid())),
            old,
            max_log_age_seconds=300,
        )
        assert status["status"] == STATUS_STALE_LOG
        assert status["alarm"] is True
        assert status["process_alive"] is True


def test_liveness_missing_log_is_lenient_while_pid_alive() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        # Log path conventions differ between launcher generations; a live pid
        # with no log must NOT false-alarm (the heartbeat check is best-effort).
        status = check_sidecar_liveness(
            _write(out / "sidecar.pid", str(os.getpid())),
            out / "sidecar.log",
        )
        assert status["status"] == STATUS_ALIVE
        assert status["alarm"] is False


def test_liveness_stale_threshold_respects_max_log_age() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        log = out / "sidecar.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("x\n", encoding="utf-8")
        os.utime(log, (time.time() - 30, time.time() - 30))
        status = check_sidecar_liveness(
            _write(out / "sidecar.pid", str(os.getpid())),
            log,
            max_log_age_seconds=15,
        )
        assert status["alarm"] is True  # 30s > 15s cap
        status2 = check_sidecar_liveness(
            out / "sidecar.pid",
            log,
            max_log_age_seconds=300,
        )
        assert status2["alarm"] is False  # 30s <= 300s cap


def test_liveness_cli_prints_parseable_json_and_exit_code() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        pidfile = _write(out / "sidecar.pid", str(os.getpid()))
        logfile = _fresh_log(out / "sidecar.log")
        proc = subprocess.run(
            [sys.executable, str(LIVENESS), "--pidfile", str(pidfile), "--log", str(logfile)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        status = json.loads(proc.stdout)
        assert status["alive"] is True
        # Dead pid -> exit 1 (grep-able failure for bash callers).
        proc2 = subprocess.run(
            [
                sys.executable,
                str(LIVENESS),
                "--pidfile",
                str(_write(out / "dead.pid", "999999999")),
                "--log",
                str(logfile),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc2.returncode == 1
        assert json.loads(proc2.stdout)["alarm"] is True


def test_default_sidecar_log_path_mirrors_launcher_convention(
    monkeypatch,
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        # Simulate the box layout: logs/sapo_27b_ai exists -> the launcher
        # convention (logs/sapo_27b_ai/repair_sidecar_<suffix>.log) wins.
        (Path(tmp) / "logs" / "sapo_27b_ai").mkdir(parents=True)
        monkeypatch.chdir(tmp)
        out = Path(tmp) / "outputs" / "sapo-27b-ai-20260826T093441"
        candidate = default_sidecar_log_path(out)
        assert candidate.name == "repair_sidecar_20260826T093441.log"
        assert str(candidate).endswith("logs/sapo_27b_ai/repair_sidecar_20260826T093441.log")
        # No logs dir -> graceful fallback inside the output dir.
        import shutil

        shutil.rmtree(Path(tmp) / "logs")
        monkeypatch.chdir(tmp)
        out2 = Path(tmp) / "other" / "run123"
        assert default_sidecar_log_path(out2).name == "repair_sidecar.log"


# ---------------------------------------------------------------------------
# 2. ensure script: idempotent boot guard, relaunch on SIGKILL death
# ---------------------------------------------------------------------------


def _run_ensure(out: Path, logdir: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["REPAIR_POLL_SECONDS"] = "2"
    env["REPAIR_LIMIT"] = "20"
    return subprocess.run(
        ["bash", str(ENSURE), str(out), str(logdir)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(ROOT),
    )


def test_ensure_relaunches_sigkilled_sidecar_and_is_idempotent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        logdir = Path(tmp) / "logs"
        out.mkdir(parents=True, exist_ok=True)

        # Fresh OUT: no sidecar anywhere -> ensure must spawn one.
        first = _run_ensure(out, logdir)
        assert first.returncode == 0, first.stdout + first.stderr
        pidfile = out / "repair_sidecar.pid"
        assert pidfile.exists()
        pid1 = int(pidfile.read_text(encoding="utf-8").strip())
        assert pid1 > 0
        time.sleep(2.5)  # let the sidecar pass its first sleep cycle
        assert os.kill(pid1, 0) == 0 or _pid_exists(pid1)

        # Idempotent: alive sidecar -> ensure is a no-op, same pid.
        second = _run_ensure(out, logdir)
        assert second.returncode == 0, second.stdout + second.stderr
        assert int(pidfile.read_text(encoding="utf-8").strip()) == pid1
        assert "SIDECAR_ALIVE" in second.stdout
        assert "SIDECAR_DEAD_ALARM" not in second.stdout

        # Reproduce the defect: SIGKILL (untrappable, silent) exactly like the
        # box-prep cleanup loops. Pidfile is left behind.
        os.kill(pid1, signal.SIGKILL)
        time.sleep(0.5)
        assert not _pid_exists(pid1)

        # Ensure must detect the silent death and relaunch.
        third = _run_ensure(out, logdir)
        assert third.returncode == 0, third.stdout + third.stderr
        assert "SIDECAR_DEAD_ALARM" in third.stdout, third.stdout
        assert "SIDECAR_RELAUNCHED" in third.stdout, third.stdout
        pid2 = int(pidfile.read_text(encoding="utf-8").strip())
        assert pid2 != pid1
        time.sleep(2.5)
        assert _pid_exists(pid2)

        # The relaunched sidecar must actually heartbeat (fresh log) — the
        # exact thing the guard checks in production.
        log = logdir / f"repair_sidecar_{out.name}.log"
        assert log.exists()
        age = time.time() - log.stat().st_mtime
        assert age < 30, f"sidecar log too stale: {age:.0f}s"

        # Cleanup.
        _kill_quietly(pid2)


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _kill_quietly(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.3)
    except ProcessLookupError:
        pass
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


# ---------------------------------------------------------------------------
# 3. launcher + trainer pins: the guard is wired into the boot path
# ---------------------------------------------------------------------------


def test_launcher_pins_boot_guard_invocation() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    assert "sapo_ensure_repair_sidecar.sh" in source
    assert '"$NAS_ROOT/scripts/sapo_ensure_repair_sidecar.sh" "$OUT" "$LOGDIR"' in source
    assert "SIDECAR_DEAD_ALARM" in source or "boot guard" in source


def test_launcher_requires_guard_files() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    assert '"$NAS_ROOT/scripts/sapo_ensure_repair_sidecar.sh"' in source
    assert '"$NAS_ROOT/training/sidecar_liveness.py"' in source


def test_trainer_pins_liveness_guard_flags_and_step_record_field() -> None:
    trainer = ROOT / "training" / "grpo_trainer.py"
    source = trainer.read_text(encoding="utf-8")
    assert '"--repair-sidecar-pidfile"' in source
    assert '"--repair-sidecar-log"' in source
    assert '"--repair-sidecar-max-log-age"' in source
    assert 'step_ctx["sidecar_alive"]' in source
    assert 'sidecar_alive=ctx.get("sidecar_alive")' in source
    # The alarm marker is imported from the shared module (single source of
    # truth for the grep-able marker) and used in the boot + per-step alarms.
    assert "from training.sidecar_liveness import" in source
    assert "ALARM_MARKER" in source
    assert "check_sidecar_liveness(" in source


def test_record_builder_persists_sidecar_alive_flag() -> None:
    utils = ROOT / "training" / "grpo_utils.py"
    source = utils.read_text(encoding="utf-8")
    assert "sidecar_alive: bool | None = None" in source
    assert 'record["sidecar_alive"] = bool(sidecar_alive)' in source

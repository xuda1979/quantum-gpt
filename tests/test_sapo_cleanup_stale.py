"""Guards for the pre-launch stale-proc cleanup (scripts/sapo_cleanup_stale.sh).

Class-extinction (executor defect 2026-08-27): the old cleanup SIGKILLed ANY
process matching fv_gspo_repair_sidecar as stale — including the NEW run's
LIVE sidecar (frozen log -> silent starvation -> breaker stopping a healthy
trainer; killed runs 11/12). These tests pin the three guards:
  G0: live repair_sidecar.pid under the outputs root -> kill loop skipped.
  G1: trainer process alive -> kill loop skipped.
  G2: protected run dir's sidecar is NEVER matched; --stale-run targets only
      the specific stale dir.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sapo_cleanup_stale.sh"


def _spawn_fake_sidecar(run_dir: str) -> subprocess.Popen:
    """Mimic the launcher's spawn: bash scripts/fv_gspo_repair_sidecar.sh <OUT>.

    NOTE: the body must be a loop (not a bare sleep) — bash exec-optimizes
    `bash -c 'sleep 300' ...` into plain `sleep`, dropping the fake argv from
    the visible cmdline and breaking pgrep -f matching.
    """
    return subprocess.Popen(
        ["bash", "-c", "while :; do sleep 1; done", "scripts/fv_gspo_repair_sidecar.sh", run_dir]
    )


def _spawn_fake_trainer() -> subprocess.Popen:
    return subprocess.Popen(["bash", "-c", "while :; do sleep 1; done", "training/grpo_trainer.py"])


def _run_cleanup(outputs_root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), "--outputs-root", str(outputs_root), *extra],
        capture_output=True,
        text=True,
        timeout=60,
    )


def _wait_dead(proc: subprocess.Popen, timeout_s: float = 5.0) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if proc.poll() is not None:
            return True
        time.sleep(0.1)
    return False


def _outputs(tmp_path: Path) -> Path:
    root = tmp_path / "outputs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_cleanup_never_kills_sidecar_outside_this_outputs_root(tmp_path) -> None:
    """G3 (repairq 2026-09-01): the kill loop is scoped to THIS outputs root.

    The pgrep match ('fv_gspo_repair_sidecar.sh') is global: a live sidecar
    whose run dir is OUTSIDE --outputs-root (a concurrent run's sidecar, or a
    test-harness sidecar under a pytest tmp dir) was SIGKILLed by cleanup —
    the runs-11/12 defect class this file documents, and the flaky killer of
    test_sidecar_liveness_guard.py's REAL sidecars whenever the two suites
    run in the same session or concurrently on one box.
    """
    out = _outputs(tmp_path)
    stale_run = str(out / "sapo-27b-ai-DEAD")
    outside_run = str(tmp_path / "elsewhere" / "other-run")
    stale = _spawn_fake_sidecar(stale_run)
    outside = _spawn_fake_sidecar(outside_run)
    time.sleep(0.3)
    try:
        r = _run_cleanup(out)
        assert r.returncode == 0, r.stderr
        assert _wait_dead(stale), "in-root stale sidecar must still be killed"
        assert outside.poll() is None, "G3: sidecar outside this outputs root must never be killed"
    finally:
        for p in (stale, outside):
            if p.poll() is None:
                p.kill()


def test_cleanup_kills_stale_but_preserves_protected_run_sidecar(tmp_path) -> None:
    out = _outputs(tmp_path)
    stale_run = str(out / "sapo-27b-ai-DEAD")
    live_run = str(out / "sapo-27b-ai-LIVE")
    stale = _spawn_fake_sidecar(stale_run)
    live = _spawn_fake_sidecar(live_run)
    time.sleep(0.3)
    try:
        r = _run_cleanup(out, "--protect-run", live_run)
        assert r.returncode == 0, r.stderr
        assert live.poll() is None, "G2: protected live sidecar must survive"
        assert _wait_dead(stale), "stale sidecar (other run dir) must be killed"
    finally:
        for p in (stale, live):
            if p.poll() is None:
                p.kill()


def test_cleanup_skips_everything_when_trainer_alive(tmp_path) -> None:
    out = _outputs(tmp_path)
    trainer = _spawn_fake_trainer()
    stale = _spawn_fake_sidecar(str(out / "sapo-27b-ai-DEAD"))
    time.sleep(0.3)
    try:
        r = _run_cleanup(out)
        assert r.returncode == 0, r.stderr
        assert "G1 skip" in r.stdout
        assert trainer.poll() is None
        assert stale.poll() is None, "G1: nothing may be killed while a trainer is alive"
    finally:
        for p in (trainer, stale):
            if p.poll() is None:
                p.kill()


def test_cleanup_skips_everything_when_live_sidecar_pidfile_exists(tmp_path) -> None:
    out = _outputs(tmp_path)
    live = _spawn_fake_sidecar(str(out / "sapo-27b-ai-LIVE"))
    time.sleep(0.3)
    pidfile = out / "sapo-27b-ai-LIVE" / "repair_sidecar.pid"
    pidfile.parent.mkdir(parents=True, exist_ok=True)
    pidfile.write_text(str(live.pid))
    try:
        r = _run_cleanup(out)
        assert r.returncode == 0, r.stderr
        assert "G0 skip" in r.stdout
        assert live.poll() is None, "G0: live pidfile -> kill loop must not run"
    finally:
        if live.poll() is None:
            live.kill()


def test_cleanup_stale_run_targets_only_the_specific_dir(tmp_path) -> None:
    out = _outputs(tmp_path)
    target_run = str(out / "sapo-27b-ai-TARGET")
    other_run = str(out / "sapo-27b-ai-OTHER")
    target = _spawn_fake_sidecar(target_run)
    other = _spawn_fake_sidecar(other_run)
    time.sleep(0.3)
    try:
        r = _run_cleanup(out, "--stale-run", target_run)
        assert r.returncode == 0, r.stderr
        assert _wait_dead(target), "--stale-run target must be killed"
        assert other.poll() is None, "non-target sidecar must survive"
    finally:
        for p in (target, other):
            if p.poll() is None:
                p.kill()

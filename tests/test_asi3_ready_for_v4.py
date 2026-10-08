from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "harness" / "state" / "probes" / "asi3_ready_for_v4.json"


def test_probe_file_exists() -> None:
    """RED: readiness probe must exist after C-9177 completes."""
    assert PROBE.exists(), f"Expected probe at {PROBE}"


def test_probe_has_ready_true() -> None:
    """The probe must declare ready=true for v4 launch to proceed."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert data.get("ready") is True, f"Expected ready=true, got {data.get('ready')}"


def test_probe_has_checked_utc() -> None:
    """The probe must record when it was checked."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert "checked_utc" in data, "Missing checked_utc timestamp"
    assert len(data["checked_utc"]) > 0, "checked_utc must not be empty"


def test_probe_has_disk_free_gb() -> None:
    """The probe must record available disk space (must be >= 50 GB)."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    disk_free = data.get("disk_free_gb")
    assert disk_free is not None, "Missing disk_free_gb"
    assert isinstance(disk_free, (int, float)), f"disk_free_gb must be numeric, got {type(disk_free)}"
    assert disk_free >= 50, f"Need >=50 GB free, got {disk_free} GB"


def test_probe_has_zombie_clean_true() -> None:
    """The probe must confirm zombie cleanup is complete."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert data.get("zombie_clean") is True, f"Expected zombie_clean=true, got {data.get('zombie_clean')}"


def test_probe_has_box_health_ok() -> None:
    """The probe must confirm ASI3 box health endpoint returns ok=true."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert data.get("box_health_ok") is True, f"Expected box_health_ok=true, got {data.get('box_health_ok')}"


def test_probe_has_no_orphan_processes() -> None:
    """The probe must confirm no orphan training processes on the box."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert data.get("orphan_processes_clean") is True, (
        f"Expected orphan_processes_clean=true, got {data.get('orphan_processes_clean')}"
    )


def test_probe_has_pid_81128_dead() -> None:
    """The probe must confirm PID 81128 (prior train fire) is dead."""
    data = json.loads(PROBE.read_text(encoding="utf-8"))
    assert data.get("pid_81128_dead") is True, f"Expected pid_81128_dead=true, got {data.get('pid_81128_dead')}"

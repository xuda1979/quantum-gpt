"""Tests for scripts/sapo_wedge_watch.py — the unarmed wedge detector
(keepalive.md audit 2026-09-01: proposed detector never landed; the ASI3
busy-wedge class recurred 23:06 with busyAgeMs 699,817 / pendingRequestCount
12). Pins the wedge classification contract; the detector only ALARMS (log
line) — the keeper owns relaunch.
"""

from __future__ import annotations  # py3.9-safe (PEP 604) annotations

from unittest import mock

from scripts.sapo_wedge_watch import (
    DEFAULT_BUSY_AGE_MS_MAX,
    classify_health,
    probe_health,
    wedge_alarms,
)

# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate


def test_wedge_alarms_busy_old_age_fires() -> None:
    """busy=true AND busyAgeMs>120000 = the ASI3 23:06 wedge class (699,817ms)
    — must fire with the age in the message."""
    health = {"busy": True, "busyAgeMs": 699817, "pendingRequestCount": 1}
    alarms = wedge_alarms(health)
    assert any("busy" in a and "699817" in a for a in alarms)


def test_wedge_alarms_pending_backlog_fires() -> None:
    """pendingRequestCount > 3 = backlog wedge (the 23:06 count was 12)."""
    health = {"busy": False, "busyAgeMs": 0, "pendingRequestCount": 12}
    alarms = wedge_alarms(health)
    assert any("pending" in a and "12" in a for a in alarms)


def test_wedge_alarms_busy_young_is_ok() -> None:
    """busy but young (busyAgeMs below the threshold) is a normal in-flight
    command — must NOT alarm."""
    health = {"busy": True, "busyAgeMs": 30_000, "pendingRequestCount": 1}
    assert wedge_alarms(health) == []


def test_wedge_alarms_idle_is_ok() -> None:
    health = {"busy": False, "busyAgeMs": 0, "pendingRequestCount": 0}
    assert wedge_alarms(health) == []


def test_wedge_alarms_missing_fields_never_alarm() -> None:
    """A health payload with missing/unknown fields must be conservative:
    never fire a wedge alarm on a partial read (parse failures are logged as
    UNKNOWN by the caller, not escalated)."""
    assert wedge_alarms({}) == []
    assert wedge_alarms({"ready": False}) == []
    assert wedge_alarms({"busy": True}) == []


def test_wedge_alarms_boundary_pending_equal_max_is_ok() -> None:
    """pendingRequestCount == 3 (the max) is NOT a backlog yet — strict >."""
    health = {"busy": False, "busyAgeMs": 0, "pendingRequestCount": 3}
    assert wedge_alarms(health) == []


def test_wedge_alarms_boundary_busy_age_exactly_max_is_ok() -> None:
    """busyAgeMs == 120000 exactly is NOT over the threshold — strict >."""
    health = {"busy": True, "busyAgeMs": DEFAULT_BUSY_AGE_MS_MAX, "pendingRequestCount": 0}
    assert wedge_alarms(health) == []


def test_wedge_alarms_custom_thresholds() -> None:
    health = {"busy": True, "busyAgeMs": 30_000, "pendingRequestCount": 0}
    assert wedge_alarms(health, busy_age_ms_max=20_000) != []
    assert wedge_alarms(health, busy_age_ms_max=60_000) == []


def test_classify_health_states() -> None:
    """3-state discipline (keepalive): ALIVE (health responds), DEAD
    (connection refused), UNKNOWN (parse failure) — plus WEDGED when a wedge
    alarm fires. The detector never kills; it reports."""
    assert classify_health({"busy": False, "busyAgeMs": 0, "pendingRequestCount": 0}) == "ok"
    assert (
        classify_health({"busy": True, "busyAgeMs": 999_999, "pendingRequestCount": 0}) == "wedged"
    )
    assert classify_health({"busy": False, "busyAgeMs": 0, "pendingRequestCount": 9}) == "wedged"


def test_probe_health_ok_and_refused() -> None:
    """probe_health returns (health_dict, state) — "ok" on HTTP 200,
    "down" on connection refusal (keeper's job to relaunch), "unknown" on
    any other transport failure. Never raises."""

    def _ok(*_a, **_k):
        class _R:
            status = 200

            def read(self):
                return b'{"busy": false, "busyAgeMs": 0, "pendingRequestCount": 0}'

            def __enter__(self):
                return self

            def __exit__(self, *_x):
                return False

        return _R()

    with mock.patch("urllib.request.urlopen", _ok):
        health, state = probe_health("http://127.0.0.1:19005")
    assert state == "ok"
    assert health["busy"] is False

    def _refused(*_a, **_k):
        raise ConnectionRefusedError("refused")

    with mock.patch("urllib.request.urlopen", _refused):
        _health, state = probe_health("http://127.0.0.1:19004")
    assert state == "down"

    def _bomb(*_a, **_k):
        raise OSError("transport exploded")

    with mock.patch("urllib.request.urlopen", _bomb):
        _health, state = probe_health("http://127.0.0.1:19004")
    assert state == "unknown"


def test_probe_health_non_json_is_unknown() -> None:
    def _ok(*_a, **_k):
        class _R:
            status = 200

            def read(self):
                return b"not json at all"

            def __enter__(self):
                return self

            def __exit__(self, *_x):
                return False

        return _R()

    with mock.patch("urllib.request.urlopen", _ok):
        health, state = probe_health("http://127.0.0.1:19005")
    assert state == "unknown"
    assert health is None

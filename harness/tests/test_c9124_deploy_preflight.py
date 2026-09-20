"""C-9124 RED tests: fail-closed deploy preflight for ASI2 :19004 deploy-class launches.

Crash class banked in harness/state/probes/c9124_evidence_500_class.json:
daemon /exec returns HTTP 500 mid-freeze-deploy (dead page / busy wedge), then
port refused; launcher dies on uncaught HTTPError 500 mid base64 -d.
Preflight must REFUSE while the signature is present: health not ready, low
uptime (boot-restart class), exec echo dead, daemon pid changed within lookback,
or local 500-class evidence newer than the lookback window.
"""

import json
import os

import pytest

from harness.asi2_deploy_preflight import (
    CRASH_SIGNATURE_PATTERNS,
    parse_health,
    preflight,
    scan_crash_signature,
)

NOW = 1758000000.0  # fixed epoch for determinism


def iso(epoch):
    import datetime

    dt = datetime.datetime.utcfromtimestamp(epoch)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def healthy(pid=85713, uptime=3000, ready=True, ok=True):
    return json.dumps(dict(ok=ok, ready=ready, pid=pid, uptime=uptime))


def run_preflight(
    tmp_path,
    health_text=None,
    health_raises=None,
    echo="C9124_PREFLIGHT_ECHO",
    pid_state=None,
    scan_files=None,
    now=NOW,
):
    calls = dict(n=0)

    def health_fn():
        if health_raises is not None:
            raise health_raises
        return health_text if health_text is not None else healthy()

    def echo_fn(marker):
        calls[n_key()] = calls.get(n_key(), 0) + 1
        if isinstance(echo, Exception):
            raise echo
        return echo

    return preflight(
        health_fn=health_fn,
        exec_echo_fn=echo_fn,
        now=now,
        state_path=str(tmp_path / "c9124_pid_state.json"),
        scan_paths=scan_files or [],
    )


def n_key():
    return "echo_calls"


def test_signature_patterns_cover_named_500_class():
    blob = " ".join(CRASH_SIGNATURE_PATTERNS)
    for needle in (
        "HTTPError 500",
        "Terminal never showed command markers",
        "Target page, context or browser has been closed",
    ):
        assert needle in blob


def test_scan_matches_recent_signature():
    lines = [iso(NOW - 60) + " HTTPError 500 mid deploy"]
    matches = scan_crash_signature(lines, now=NOW, lookback_s=7200.0)
    assert len(matches) == 1


def test_scan_ignores_expired_signature():
    lines = [iso(NOW - 3 * 3600) + " HTTPError 500 mid deploy"]
    assert scan_crash_signature(lines, now=NOW, lookback_s=7200.0) == []


def test_scan_undated_signature_fails_closed():
    lines = ["base64 -d failed: Internal Server Error"]
    assert len(scan_crash_signature(lines, now=NOW, lookback_s=7200.0)) == 1


def test_parse_health_ok_and_bad():
    h = parse_health(healthy(pid=7, uptime=42))
    assert h["ready"] is True and h["pid"] == 7 and h["uptime"] == 42
    with pytest.raises(ValueError):
        parse_health("<html>Gateway Timeout</html>")


def test_preflight_allow_happy_path(tmp_path):
    verdict = run_preflight(tmp_path)
    assert verdict["allow"] is True, verdict
    state = json.loads(open(str(tmp_path / "c9124_pid_state.json")).read())
    assert state["prev_pid"] == 85713


def test_preflight_refuses_health_unreachable(tmp_path):
    verdict = run_preflight(tmp_path, health_raises=OSError("conn refused"))
    assert verdict["allow"] is False
    assert any("health" in r for r in verdict["reasons"])


def test_preflight_refuses_not_ready(tmp_path):
    verdict = run_preflight(tmp_path, health_text=healthy(ready=False))
    assert verdict["allow"] is False


def test_preflight_refuses_low_uptime(tmp_path):
    verdict = run_preflight(tmp_path, health_text=healthy(uptime=100))
    assert verdict["allow"] is False
    assert any("uptime" in r for r in verdict["reasons"])


def test_preflight_refuses_echo_dead(tmp_path):
    verdict = run_preflight(tmp_path, echo="SOMETHING ELSE")
    assert verdict["allow"] is False
    assert any("echo" in r for r in verdict["reasons"])


def test_preflight_refuses_echo_raises(tmp_path):
    verdict = run_preflight(tmp_path, echo=TimeoutError("exec wedge"))
    assert verdict["allow"] is False


def test_preflight_refuses_recent_local_500_evidence(tmp_path):
    f = tmp_path / "launch_w_recent.log"
    f.write_text("2026-09-20T04:48:30Z urllib.error.HTTPError: HTTP Error 500\n")
    verdict = run_preflight(tmp_path, scan_files=[str(f)])
    assert verdict["allow"] is False
    assert any("500" in r or "signature" in r for r in verdict["reasons"])


def test_preflight_allows_expired_local_500_evidence(tmp_path):
    f = tmp_path / "launch_w_old.log"
    f.write_text("urllib.error.HTTPError: HTTP Error 500\n")
    old = NOW - 3 * 3600
    os.utime(str(f), (old, old))
    verdict = run_preflight(tmp_path, scan_files=[str(f)])
    assert verdict["allow"] is True, verdict


def test_preflight_refuses_pid_change_within_lookback(tmp_path):
    sp = str(tmp_path / "c9124_pid_state.json")
    json.dump(dict(prev_pid=70603, seen_epoch=NOW - 300), open(sp, "w"))
    verdict = run_preflight(tmp_path, pid_state=sp)
    assert verdict["allow"] is False
    assert any("pid" in r for r in verdict["reasons"])

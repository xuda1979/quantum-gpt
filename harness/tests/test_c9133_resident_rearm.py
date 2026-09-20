"""C-9133: wire the C-9098 window re-arm into the resident tick runner.

RED first 2026-09-20: the C-9098 run_rearm/--rearm fix is landed and
live-verified but only callable BY HAND -- the resident tick (qgh tick)
never invokes it, so window_open.json ages past the C-9071 freshness bar
(1800s) and every launch leg re-SKIPs on window=window_open_stale (EVENTS
2026-09-20T05:01:55Z, window_pid 70603, while ASI2 sat ready). Contract
under test:
  - the resident runner observing a STALE window_open artifact invokes the
    C-9098 re-arm path with no manual step;
  - after a re-arm that opens the window, the next C-9071 gate evaluation
    no longer reports window_open_stale;
  - a FRESH window never triggers a re-arm (no spurious re-arms), a
    missing/not-open artifact is not the stale trigger, and an
    already-running re-arm is never double-spawned (single flight);
  - re-arm failure is fail-closed: the gate keeps reading
    window_open_stale (SKIP) -- nothing fakes a fresh window.
All I/O is tmp-path; spawn and liveness are injected fakes.
"""

import inspect
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_preflight_gate as G  # noqa: E402
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402

NOW = 1_800_000_000.0
FRESH_S = 1800.0


def _iso(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def _write_window(tmp_path, generated_utc, artifact="window_open"):
    d = tmp_path / "c9061"
    d.mkdir(parents=True, exist_ok=True)
    (d / "window_open.json").write_text(
        json.dumps(dict(card="C-9098", artifact=artifact, generated_utc=generated_utc)) + "\n"
    )


def _gate_ctx(tmp_path):
    return G.make_ctx(
        tmp_path / "c9061",
        tmp_path / "preflights",
        tmp_path / "c9071",
        tmp_path / "state",
        clock=lambda: NOW,
    )


def _spy_spawn():
    calls = []

    def fn():
        calls.append(1)
        return 424242

    return calls, fn


def _run(tmp_path, spawn_fn, **kw):
    kw.setdefault("state_dir", str(tmp_path))
    kw.setdefault("clock", lambda: NOW)
    kw.setdefault("window_fresh_s", FRESH_S)
    return qgh.auto_rearm_stale_window(spawn_fn=spawn_fn, **kw)


def test_stale_window_triggers_rearm_no_manual_step(tmp_path):
    """Age > window_fresh_s => the runner invokes the re-arm path itself."""
    _write_window(tmp_path, _iso(NOW - FRESH_S - 200))  # 2000s old, bar 1800s
    calls, fn = _spy_spawn()
    res = _run(tmp_path, fn)
    assert res["action"] == "spawned", res
    assert len(calls) == 1, calls
    assert res.get("pid") == 424242


def test_fresh_window_does_not_rearm(tmp_path):
    """No spurious re-arms: a fresh artifact never spawns the sentinel."""
    _write_window(tmp_path, _iso(NOW - 100))
    calls, fn = _spy_spawn()
    res = _run(tmp_path, fn)
    assert res["action"] == "fresh", res
    assert calls == [], calls


def test_missing_or_not_open_artifact_is_not_the_stale_trigger(tmp_path):
    """Absent window_open / window_not_open artifact => no re-arm decision
    from THIS card (that failure mode is owned elsewhere; fail closed)."""
    calls, fn = _spy_spawn()
    res = _run(tmp_path, fn)  # nothing written at all
    assert res["action"] == "no-artifact", res
    assert calls == [], calls
    _write_window(tmp_path, _iso(NOW - FRESH_S - 999), artifact="window_not_open")
    res = _run(tmp_path, fn)
    assert res["action"] == "no-artifact", res
    assert calls == [], calls


def test_after_rearm_opens_gate_no_longer_reports_window_open_stale(tmp_path):
    """The acceptance chain: stale -> re-arm (bar met, artifact rewritten
    fresh exactly as run_rearm's bar-met poll does) -> the NEXT gate
    evaluation has NO window_open_stale unmet."""
    _write_window(tmp_path, _iso(NOW - FRESH_S - 200))

    def rearm_opens():
        _write_window(tmp_path, _iso(NOW))  # run_rearm bar-met rewrite
        return 424242

    res = _run(tmp_path, rearm_opens)
    assert res["action"] == "spawned", res
    verdict, _path, detail = G.evaluate(_gate_ctx(tmp_path))
    assert "window_open_stale" not in json.dumps(detail["unmet"]), detail["unmet"]
    assert "window" not in detail["unmet"], detail["unmet"]


def test_rearm_failure_leaves_gate_skip_fail_closed(tmp_path):
    """A re-arm that expires WITHOUT opening (run_rearm's failure terminal:
    window_not_open.json, window_open.json untouched) must leave the gate
    SKIP on window_open_stale -- nothing fakes a fresh window."""
    _write_window(tmp_path, _iso(NOW - FRESH_S - 200))

    def rearm_fails():
        d = tmp_path / "c9061"
        (d / "window_not_open.json").write_text(
            json.dumps(dict(card="C-9098", artifact="window_not_open", reason="rearm-expired"))
            + "\n"
        )
        return 424242

    res = _run(tmp_path, rearm_fails)
    assert res["action"] == "spawned", res
    verdict, _path, detail = G.evaluate(_gate_ctx(tmp_path))
    assert verdict == "SKIP", verdict
    assert detail["unmet"].get("window") == "window_open_stale", detail["unmet"]


def test_spawn_crash_is_fail_closed_and_events(tmp_path):
    """A spawn error must never unwind the tick and must never touch the
    window artifact: gate still SKIP on window_open_stale; an event names
    the failure."""
    _write_window(tmp_path, _iso(NOW - FRESH_S - 200))

    def boom():
        raise OSError("no fork")

    res = _run(tmp_path, boom)
    assert res["action"] == "spawn-failed", res
    verdict, _path, detail = G.evaluate(_gate_ctx(tmp_path))
    assert detail["unmet"].get("window") == "window_open_stale", detail["unmet"]
    events = tmp_path / "EVENTS.jsonl"  # event(state_dir=...) writes HERE
    assert events.exists() and "c9133_rearm_spawn_failed" in events.read_text()


def test_single_flight_no_double_rearm(tmp_path):
    """An already-running re-arm is never double-spawned (B-087 herd law)."""
    _write_window(tmp_path, _iso(NOW - FRESH_S - 200))
    calls, fn = _spy_spawn()
    res = _run(tmp_path, fn, is_running_fn=lambda: True)
    assert res["action"] == "already-running", res
    assert calls == [], calls


def test_rearm_running_lock_liveness(tmp_path):
    """The single-flight check is pid+lstart live (pid-reuse guard), not a
    bare lockfile existence check."""
    lock = tmp_path / "locks" / "c9098-rearm.json"
    lock.parent.mkdir(parents=True, exist_ok=True)
    # live pid with matching lstart -> running
    lock.write_text(json.dumps(dict(pid=os.getpid(), lstart=H.process_lstart(os.getpid()))) + "\n")
    assert qgh._rearm_running(str(lock)) is True
    # pid-reuse guard: lstart mismatch -> NOT running
    lock.write_text(json.dumps(dict(pid=os.getpid(), lstart="1970-01-01T00:00:00Z")) + "\n")
    assert qgh._rearm_running(str(lock)) is False
    # dead pid -> NOT running (lock purge-eligible, re-arm may respawn)
    lock.write_text(json.dumps(dict(pid=2**22, lstart="2026-09-20T00:00:00Z")) + "\n")
    assert qgh._rearm_running(str(lock)) is False
    # corrupt/absent -> NOT running (fail open to a NEW spawn, never a lie)
    lock.write_text("not json{")
    assert qgh._rearm_running(str(lock)) is False
    assert qgh._rearm_running(str(tmp_path / "locks" / "absent.json")) is False


def test_resident_tick_wires_the_rearm_step():
    """The wiring is IN the resident tick, not a side entrypoint: cmd_tick
    must invoke the C-9133 re-arm step itself (source-level, like C-9101)."""
    src = inspect.getsource(qgh.cmd_tick)
    assert "auto_rearm_stale_window(" in src, "cmd_tick never re-arms a stale window"

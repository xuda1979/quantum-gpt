import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

# C-0051: the fire-on-ready watcher (owns C-0002's orphaned watcher role).
#
# RED 2026-09-16: no tmp/c0051_fire_on_ready.py existed -- when C-0002's
# watcher window closes nothing re-arms the fire-on-ready leg, so a
# console-cured ASI2 (C-0042) idles the objective. Contract under test:
#   ready:true + exec round-trip -> fire the fail-closed leg EXACTLY ONCE,
#   holding asi2-eval.lock (harness_lib.acquire_lock) and stamping the
#   canonical holdout+scorer sha256 pins into the box leg log;
#   ready:false or exec-dead -> NO fire + a NAMED probe record under
#   harness/state/probes/ (rate-limited: no silent retry storm);
#   fired/in-flight state survives the worker -> no duplicate fire across
#   restarts (idempotent), incl. cross-checking C-0002's own fired marker.
# All box probes are injected fakes: the suite never touches the network or
# the live asi2-eval.lock (pid 35393 holds it in the real tree right now).

ROOT = Path(__file__).resolve().parents[2]
WATCHER = ROOT / "tmp" / "c0051_fire_on_ready.py"
HEALTH = "http://127.0.0.1:19004/health"


def _load():
    spec = importlib.util.spec_from_file_location("c0051_fire_on_ready", WATCHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dead_pid():
    # A pid that is provably NOT alive (spawned, reaped, gone).
    proc = subprocess.Popen(
        [sys.executable, "-c", "pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    proc.wait()
    sys.path.insert(0, str(ROOT / "harness"))
    import harness_lib

    assert not harness_lib.pid_alive(proc.pid)
    return proc.pid


def mk(
    tmp_path,
    health=None,
    health_exc=None,
    exec_out="C0051_OK",
    exec_exc=None,
    launcher_rc=0,
    launcher_stdout="",
    launcher_stderr="",
    probe_every_s=300.0,
):
    # Build a fully injected watcher context on tmp paths.
    mod = _load()
    exec_calls, launcher_calls = [], []

    def get_json(url, timeout=8):
        if health_exc is not None:
            raise health_exc
        assert url == HEALTH
        return health

    def exec_fn(cmd, wait_ms=90000, timeout=130, port=None):
        exec_calls.append(cmd)
        if exec_exc is not None:
            raise exec_exc
        return exec_out

    def launcher():
        launcher_calls.append(1)
        return subprocess.CompletedProcess(
            [], launcher_rc, stdout=launcher_stdout, stderr=launcher_stderr
        )

    ctx = mod.make_ctx(
        lock_path=str(tmp_path / "asi2-eval.lock"),
        state_path=str(tmp_path / "c0051_watcher_state.json"),
        fired_path=str(tmp_path / "c0051_fired.json"),
        probe_dir=str(tmp_path / "probes"),
        c0002_fired_path=str(tmp_path / "c0002_fired.json"),
        get_json=get_json,
        exec_fn=exec_fn,
        launcher=launcher,
        cutoff=mod.now().replace(year=2099),
        probe_every_s=probe_every_s,
    )
    ctx._test = dict(exec_calls=exec_calls, launcher_calls=launcher_calls)
    return mod, ctx


def probes_for(tmp_path, reason=None):
    out = []
    for p in Path(tmp_path / "probes").glob("C-0051-*.json"):
        d = json.loads(p.read_text())
        if reason is None or d.get("reason") == reason:
            out.append((p.name, d))
    return out


# ------------------------------------------------------------------ fire path
def test_ready_and_exec_ok_fires_leg_exactly_once_and_stamps_shas(tmp_path):
    mod, ctx = mk(
        tmp_path,
        health=dict(ready=True, pid=99),
        launcher_stdout="LEG_LAUNCHED step=100 adapter=/a log=/tmp/leg_c0002_step100.log\n",
    )
    tok = mod.arm(ctx)
    assert tok and Path(ctx.lock_path).exists()  # lock taken via harness_lib

    action, reason = mod.poll_once(ctx)
    assert (action, reason) == ("fire", "ready+exec-ok")
    assert ctx._test["launcher_calls"] == []
    rc = mod.dispatch(ctx)
    assert rc == 0
    assert ctx._test["launcher_calls"] == [1]  # EXACTLY once
    fired = json.loads(Path(ctx.fired_path).read_text())
    assert fired["rc"] == 0 and fired["box_log"] == "/tmp/leg_c0002_step100.log"

    # sha pins stamped into the box leg log, matching the canonical freeze
    fz = mod._freeze_module()
    manifest = dict(fz.load_manifest(str(ROOT / fz.MANIFEST_RELPATH)))
    stamps = [c for c in ctx._test["exec_calls"] if "SHA256" in c]
    assert any(
        "leg_c0002_step100.log" in c and "HOLDOUT_SHA256=" + manifest[fz.BENCH_RELPATH] in c
        for c in stamps
    )
    for rel in fz.SCORER_CHAIN:
        assert any(f"SCORER_SHA256 {rel}={manifest[rel]}" in c for c in stamps)
    assert fired["stamp_ok"] is True
    mod.release(ctx, tok)
    assert not Path(ctx.lock_path).exists()


# ------------------------------------------------------------- no-fire paths
def test_not_ready_means_no_fire_plus_named_probe(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False, startupState="booting"))
    tok = mod.arm(ctx)
    action, reason = mod.poll_once(ctx)
    assert (action, reason) == ("wait", "asi2-not-ready")
    assert ctx._test["launcher_calls"] == []
    recs = probes_for(tmp_path, "asi2-not-ready")
    assert len(recs) == 1 and recs[0][1]["card"] == "C-0051"
    assert recs[0][1]["asi2_ready"] is False  # named, measured payload
    mod.release(ctx, tok)


def test_exec_dead_means_no_fire_plus_named_probe(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7), exec_exc=RuntimeError("timeout"))
    tok = mod.arm(ctx)
    action, reason = mod.poll_once(ctx)
    assert (action, reason) == ("wait", "exec-dead")
    assert ctx._test["launcher_calls"] == []
    assert len(probes_for(tmp_path, "exec-dead")) == 1
    mod.release(ctx, tok)


def test_no_silent_retry_storm_probes_rate_limited(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False), probe_every_s=300.0)
    tok = mod.arm(ctx)
    for _ in range(6):
        assert mod.poll_once(ctx)[0] == "wait"
    assert len(probes_for(tmp_path, "asi2-not-ready")) == 1  # not 6
    mod.release(ctx, tok)


# --------------------------------------------------- idempotency / restarts
def test_already_fired_state_blocks_duplicate_fire(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7))
    mod.save_json(ctx.fired_path, dict(rc=0, ts=mod.now_iso()))
    tok = mod.arm(ctx)
    assert mod.poll_once(ctx) == ("stop", "already-fired")
    assert ctx._test["launcher_calls"] == []
    mod.release(ctx, tok)


def test_c0002_fired_marker_blocks_fire_cross_watcher(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7))
    mod.save_json(ctx.c0002_fired_path, dict(rc=0, ts=mod.now_iso()))
    tok = mod.arm(ctx)
    assert mod.poll_once(ctx) == ("stop", "already-fired-c0002")
    assert ctx._test["launcher_calls"] == []
    mod.release(ctx, tok)


def test_inflight_unresolved_fails_closed_after_crash(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7))
    dead = _dead_pid()
    st = dict(pid=dead, cutoff_utc=mod.now_iso(), in_flight=dict(pid=dead, ts=mod.now_iso()))
    mod.save_json(ctx.state_path, st)
    tok = mod.arm(ctx)
    assert mod.poll_once(ctx) == ("stop", "in-flight-unresolved")
    assert ctx._test["launcher_calls"] == []  # never re-fire blind
    assert len(probes_for(tmp_path, "in-flight-unresolved")) == 1
    mod.release(ctx, tok)


# ------------------------------------------------------- arm / state / locks
def test_arm_writes_pid_and_cutoff_state(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False))
    tok = mod.arm(ctx)
    st = json.loads(Path(ctx.state_path).read_text())
    assert st["pid"] == os.getpid()
    assert mod.parse_iso(st["cutoff_utc"]).year == 2099
    mod.release(ctx, tok)


def test_arm_refuses_live_holder_lock_fail_closed(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False))
    mod.save_json(ctx.lock_path, dict(pid=os.getpid(), ts=mod.now_iso()))
    assert mod.arm(ctx) is None  # live holder (this test proc): never steal
    assert len(probes_for(tmp_path, "lock-refused")) == 1


def test_rearm_after_holder_death_takes_over(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False))
    dead = _dead_pid()
    old_ts = "2026-09-16T00:00:00Z"
    mod.save_json(ctx.lock_path, dict(pid=dead, ts=old_ts))
    tok = mod.arm(ctx)
    assert tok is not None and tok["pid"] == os.getpid()  # crashed holder takeover
    mod.release(ctx, tok)


def test_main_cutoff_terminal_releases_lock_and_probes(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=False))
    rc = mod.main(
        ["--cutoff-mins", "-1"],
        lock_path=ctx.lock_path,
        state_path=ctx.state_path,
        fired_path=ctx.fired_path,
        probe_dir=ctx.probe_dir,
        c0002_fired_path=ctx.c0002_fired_path,
        hb_path=str(tmp_path / "hb.progress"),  # keep the REAL heartbeat clean
        get_json=ctx.get_json,
        exec_fn=ctx.exec_fn,
        launcher=ctx.launcher,
    )
    assert rc == 3  # cutoff, never fired
    assert ctx._test["launcher_calls"] == []
    assert not Path(ctx.lock_path).exists()  # released on the terminal path
    assert len(probes_for(tmp_path, "cutoff-never-ready")) == 1


# ------------------------------------------------- C-0051 r2 (this worker)
# RED first 2026-09-17: three defects found in review of the landed watcher.
# 1. arm() drops an in_flight marker on pid_alive alone; macOS recycles pids
#    (harness_lib.process_lstart docstring) -> reused pid = blind re-fire.
# 2. dispatch never re-checks asi2-eval.lock ownership; LOCK_STALE_S=1800
#    lets another card take the lock mid-window -> unserialized second leg.
# 3. main()'s stop path force-writes a same-second same-reason probe that
#    overwrites the rich fail-closed record with a thin note.


def test_pid_reuse_on_inflight_marker_fails_closed(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7))
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tok = None
    try:
        # Live pid whose lstart does NOT match the marker's record = REUSED
        # pid: the original dispatcher is gone, dispatch rc UNKNOWN.
        st = dict(
            pid=os.getpid(),
            cutoff_utc=mod.now_iso(),
            in_flight=dict(pid=proc.pid, ts=mod.now_iso(), lstart="Tue Jan  1 00:00:01 2001"),
        )
        mod.save_json(ctx.state_path, st)
        tok = mod.arm(ctx)  # arm must NOT drop the marker on pid_alive alone
        assert mod.poll_once(ctx) == ("stop", "in-flight-unresolved")
        assert ctx._test["launcher_calls"] == []  # never re-fire blind
        recs = probes_for(tmp_path, "in-flight-unresolved")
        assert len(recs) == 1 and recs[0][1]["pid_reused"] is True
    finally:
        proc.kill()
        proc.wait()
        if tok:
            mod.release(ctx, tok)


def test_dispatch_rechecks_lock_ownership_before_firing(tmp_path):
    mod, ctx = mk(
        tmp_path,
        health=dict(ready=True, pid=7),
        launcher_stdout="LEG_LAUNCHED step=1 log=/tmp/leg.log\n",
    )
    tok = mod.arm(ctx)
    foreign = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        # Live foreign holder with a fresh lease: acquire_lock refuses.
        mod.save_json(ctx.lock_path, dict(pid=foreign.pid, ts=mod.now_iso()))
        rc = mod.dispatch(ctx)
        assert rc == 4
        assert ctx._test["launcher_calls"] == []  # NO unserialized second leg
        assert len(probes_for(tmp_path, "lock-lost")) == 1
        assert not Path(ctx.fired_path).exists()
    finally:
        foreign.kill()
        foreign.wait()
    # Box free again: dispatch must re-acquire the lock and fire.
    rc = mod.dispatch(ctx)
    assert rc == 0
    assert ctx._test["launcher_calls"] == [1]
    cur = json.loads(Path(ctx.lock_path).read_text())
    assert cur["pid"] == os.getpid()  # ownership re-established
    fired = json.loads(Path(ctx.fired_path).read_text())
    assert fired["rc"] == 0
    mod.release(ctx, getattr(ctx, "_tok", tok))


def test_main_stop_probe_keeps_rich_payload_single_record(tmp_path):
    mod, ctx = mk(tmp_path, health=dict(ready=True, pid=7))
    dead = _dead_pid()
    st = dict(pid=dead, cutoff_utc=mod.now_iso(), in_flight=dict(pid=dead, ts=mod.now_iso()))
    mod.save_json(ctx.state_path, st)
    rc = mod.main(
        ["--cutoff-mins", "1"],
        lock_path=ctx.lock_path,
        state_path=ctx.state_path,
        fired_path=ctx.fired_path,
        probe_dir=ctx.probe_dir,
        c0002_fired_path=ctx.c0002_fired_path,
        hb_path=str(tmp_path / "hb.progress"),
        get_json=ctx.get_json,
        exec_fn=ctx.exec_fn,
        launcher=ctx.launcher,
        cutoff=mod.now() + mod.timedelta(seconds=3),
    )
    assert rc == 5  # terminal no-fire (unresolved in_flight)
    assert ctx._test["launcher_calls"] == []
    recs = probes_for(tmp_path, "in-flight-unresolved")
    assert len(recs) == 1  # poll record must survive main's terminal probe
    assert recs[0][1].get("in_flight") is not None  # rich payload survived

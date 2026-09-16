#!/usr/bin/env python3
# C-0051 fire-on-ready watcher (owns C-0002's orphaned watcher role).
#
# C-0002 died leaving tmp/c0002_fire_on_ready.py orphaned with a hard-coded
# 2026-09-16 cutoff: when the user cures ASI2 via console refresh (C-0042)
# nothing re-fires the fail-closed 18-task leg and the objective idles despite
# a healthy box. This watcher re-arms that behavior with the C-0051 contract:
#
#   - Fire gate = ASI2 :19004 /health ready:true AND an exec round-trip
#     (echo C0051_OK) -- a bare ready flag has already been shown to lie
#     during boot-restart loops (B-187 class), so both must hold.
#   - The leg fires EXACTLY ONCE: fired-state file + in-flight marker fail
#     closed across restarts, and C-0002's own fired marker
#     (tmp/c0002_fired.json, watcher pid 35393 was live while this was
#     written) is cross-checked so the two watchers can never double-fire.
#   - asi2-eval.lock is taken via harness_lib.acquire_lock at arm time and
#     released on EVERY terminal path (fired / cutoff / refused / crash).
#   - On fire, the canonical holdout+scorer sha256 pins (freeze manifest) are
#     stamped into the box leg log the launcher reports.
#   - No-fire observations leave a NAMED probe record under
#     harness/state/probes/ (rate-limited per reason -- no silent retry storm).
#
# Exit codes: 0 leg launched; 1 launcher precheck fail; 2 other launcher
# failure; 3 cutoff reached, never ready; 4 lock held by a live holder;
# 5 terminal no-fire (already fired / in-flight unresolved or foreign).
#
# Python 3.9-safe, stdlib only (box runtime gate). Testable: every box probe
# is injected via make_ctx; main() wires the real ones.

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "harness"))
import harness_lib  # noqa: E402

POLL_S = 30
PROBE_EVERY_S = 300.0
HEALTH_PORT = 19004
DEFAULT_CUTOFF_MINS = 240.0


def now():
    return datetime.now(timezone.utc)


def now_iso():
    return harness_lib.now_iso()


def parse_iso(s):
    return harness_lib.parse_iso(s)


# Re-exported so tests and operators use ONE io vocabulary (harness_lib).
save_json = harness_lib.save_json
load_json = harness_lib.load_json


def hb(msg, path=None):
    if not path:
        return
    harness_lib.append_line(path, now_iso() + " c0051-watcher: " + msg)


def _freeze_module():
    repo_root = str(PROJECT_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from evals.runner import holdout_freeze as fz
    return fz


def canonical_shas():
    # Canonical pins from the freeze manifest; a missing/short manifest
    # raises here -> dispatch fails the stamp loudly instead of firing
    # unpinned evidence.
    fz = _freeze_module()
    entries = dict(fz.load_manifest(str(PROJECT_ROOT / fz.MANIFEST_RELPATH)))
    hold = entries[fz.BENCH_RELPATH]
    scorers = dict()
    for rel in fz.SCORER_CHAIN:
        scorers[rel] = entries[rel]
    return hold, scorers


class Ctx(object):
    # All box contact is behind these callables: get_json (health), exec_fn
    # (daemon /exec), launcher (the fail-closed leg dispatch). Tests inject
    # fakes; main() wires the real ones.
    def __init__(self, lock_path, state_path, fired_path, probe_dir,
                 c0002_fired_path, get_json, exec_fn, launcher, cutoff,
                 port=HEALTH_PORT, probe_every_s=PROBE_EVERY_S, hb_path=None):
        self.lock_path = lock_path
        self.state_path = state_path
        self.fired_path = fired_path
        self.probe_dir = probe_dir
        self.c0002_fired_path = c0002_fired_path
        self.get_json = get_json
        self.exec_fn = exec_fn
        self.launcher = launcher
        self.cutoff = cutoff
        self.port = port
        self.probe_every_s = probe_every_s
        self.hb_path = hb_path
        self._last_probe = dict()


def make_ctx(**kw):
    return Ctx(**kw)


def write_probe(ctx, reason, payload=None, force=False):
    # Named probe record under harness/state/probes/. Rate-limited per
    # reason so a long wait does not become a silent retry storm; terminal
    # paths pass force=True.
    last = ctx._last_probe.get(reason)
    if not force and last is not None and (time.time() - last) < ctx.probe_every_s:
        return False
    ctx._last_probe[reason] = time.time()
    rec = dict(card="C-0051", reason=reason, measured_at_utc=now_iso())
    rec.update(payload or dict())
    stem = "C-0051-" + reason + "-" + now().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(ctx.probe_dir, stem + ".json")
    n = 2
    while os.path.exists(path):  # same-second same-reason: never overwrite
        path = os.path.join(ctx.probe_dir, stem + "-%d.json" % n)
        n += 1
    harness_lib.save_json(path, rec)
    return True


def arm(ctx):
    # Take the eval lock for the whole armed window (C-0002 convention: the
    # leg fires the moment ASI2 heals, and no other leg interleaves). A live
    # holder refuses us -- fail closed, named probe, no steal.
    tok = harness_lib.acquire_lock(ctx.lock_path)
    if tok is None:
        write_probe(ctx, "lock-refused", force=True,
                    payload=dict(lock=os.path.basename(ctx.lock_path),
                                 note="live holder; window aborts (no double-leg)"))
        hb("lock held by live holder; refusing to arm", ctx.hb_path)
        return None
    # State survives the worker: a prior in_flight marker with a dead pid is
    # UNRESOLVED dispatch evidence -- carry it forward so poll_once stops
    # fail-closed instead of re-firing blind (idempotency across restarts).
    prior = harness_lib.load_json(ctx.state_path) or dict()
    # NEVER drop a prior in_flight marker on pid_alive alone: macOS recycles
    # pids (harness_lib.process_lstart), so an "alive" pid may be an unrelated
    # process that reused it. poll_once fail-closes on any foreign marker.
    infl = prior.get("in_flight")
    harness_lib.save_json(ctx.state_path, dict(
        pid=os.getpid(),
        cutoff_utc=ctx.cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
        armed_utc=now_iso(),
        in_flight=infl,
    ))
    ctx._tok = tok
    hb("armed pid=" + str(os.getpid()) + " cutoff=" + ctx.cutoff.strftime("%H:%MZ"),
       ctx.hb_path)
    return tok


def release(ctx, tok):
    ok = harness_lib.release_lock(ctx.lock_path, tok)
    hb("release_lock -> " + str(ok), ctx.hb_path)
    return ok


def _already_fired(ctx):
    # Own fired state (any recorded rc) or C-0002's fired marker (rc 0):
    # either means a leg was already dispatched this window.
    fired = harness_lib.load_json(ctx.fired_path)
    if isinstance(fired, dict) and "rc" in fired:
        return "already-fired"
    c2 = harness_lib.load_json(ctx.c0002_fired_path)
    if isinstance(c2, dict) and c2.get("rc") == 0:
        return "already-fired-c0002"
    return None


def in_flight_hazard(ctx):
    # Fail-closed view of a prior in_flight marker; None = clean.
    # - pid dead: dispatch outcome UNKNOWN -> unresolved.
    # - pid alive but lstart differs from the recorded one: REUSED pid
    #   (macOS recycles pids) -> original dispatcher gone, rc UNKNOWN.
    # - pid alive and lstart matches: the original dispatcher process is
    #   still alive -- it owns the dispatch; never double-fire.
    # Only our OWN pid is clean (mid-dispatch in this process).
    st = harness_lib.load_json(ctx.state_path) or dict()
    infl = st.get("in_flight")
    if not isinstance(infl, dict) or not infl.get("pid"):
        return None
    if infl.get("pid") == os.getpid():
        return None
    alive = harness_lib.pid_alive(infl.get("pid"))
    reused = None
    if alive:
        cur = harness_lib.process_lstart(infl.get("pid"))
        rec = infl.get("lstart")
        reused = not (rec and cur and rec == cur)
    return dict(in_flight=infl, alive=alive, pid_reused=reused)


def poll_once(ctx):
    # Returns (action, reason): action in (fire, wait, stop).
    dup = _already_fired(ctx)
    if dup:
        return ("stop", dup)
    hz = in_flight_hazard(ctx)
    if hz:
        write_probe(ctx, "in-flight-unresolved", force=True, payload=dict(
            in_flight=hz["in_flight"], alive=hz["alive"],
            pid_reused=hz["pid_reused"],
            note="dispatcher alive-foreign or rc unknown (pid may be REUSED); check box leg log before any re-fire"))
        ctx._terminal_probed = "in-flight-unresolved"
        return ("stop", "in-flight-unresolved")
    try:
        h = ctx.get_json("http://127.0.0.1:" + str(ctx.port) + "/health")
    except Exception as e:  # noqa: BLE001
        write_probe(ctx, "asi2-unreachable",
                    payload=dict(err=repr(e)[:160], asi2_ready=False))
        return ("wait", "asi2-unreachable")
    if not isinstance(h, dict) or h.get("ready") is not True:
        write_probe(ctx, "asi2-not-ready", payload=dict(
            asi2_ready=False,
            startupState=(h.get("startupState") if isinstance(h, dict) else repr(h)[:60])))
        return ("wait", "asi2-not-ready")
    # ready flag alone has lied before (boot-restart loops): demand an exec
    # round-trip before trusting the box with a leg.
    try:
        out = ctx.exec_fn("echo C0051_OK", port=ctx.port)
        ok = "C0051_OK" in (out or "")
    except Exception as e:  # noqa: BLE001
        write_probe(ctx, "exec-dead", payload=dict(err=repr(e)[:160]))
        return ("wait", "exec-dead")
    if not ok:
        write_probe(ctx, "exec-dead", payload=dict(out=str(out)[:120]))
        return ("wait", "exec-dead")
    return ("fire", "ready+exec-ok")


def dispatch(ctx):
    # Fire the fail-closed leg EXACTLY ONCE and record honest evidence.
    # Serialization: re-verify we still own asi2-eval.lock RIGHT BEFORE the
    # launch -- LOCK_STALE_S=1800 lets another card take the lock mid-window
    # (armed windows are hours). Re-acquire when free; refuse while a live
    # foreign holder owns it. Never fire lockless.
    tok = getattr(ctx, "_tok", None)
    if tok is not None:
        cur = harness_lib.load_json(ctx.lock_path)
        if not (isinstance(cur, dict) and cur.get("pid") == tok.get("pid")
                and cur.get("ts") == tok.get("ts")):
            got = harness_lib.acquire_lock(ctx.lock_path)
            if got is None:
                write_probe(ctx, "lock-lost", force=True, payload=dict(
                    lock=os.path.basename(ctx.lock_path),
                    note="asi2-eval.lock no longer ours (stale takeover); refusing to fire"))
                hb("lock lost at dispatch; refusing to fire (no unserialized leg)",
                   ctx.hb_path)
                return 4
            ctx._tok = got
            hb("re-acquired asi2-eval.lock at dispatch", ctx.hb_path)
    st = harness_lib.load_json(ctx.state_path) or dict()
    st["in_flight"] = dict(pid=os.getpid(),
                           lstart=harness_lib.process_lstart(os.getpid()),
                           ts=now_iso())
    harness_lib.save_json(ctx.state_path, st)
    try:
        p = ctx.launcher()
    except Exception as e:  # noqa: BLE001
        # Launcher never dispatched: clear the marker, this IS retryable.
        st = harness_lib.load_json(ctx.state_path) or dict()
        st["in_flight"] = None
        harness_lib.save_json(ctx.state_path, st)
        write_probe(ctx, "launcher-crashed", force=True,
                    payload=dict(err=repr(e)[:200]))
        hb("launcher crashed pre-dispatch: " + repr(e)[:120], ctx.hb_path)
        return 2
    rc = getattr(p, "returncode", 2)
    stdout = getattr(p, "stdout", "") or ""
    box_log = None
    step = None
    stamp_ok = None
    if rc == 0:
        m = re.search(r"log=(\S+)", stdout)
        box_log = m.group(1) if m else None
        m2 = re.search(r"step=(\S+)", stdout)
        step = m2.group(1) if m2 else None
        stamp_ok = False
        if box_log:
            try:
                hold, scorers = canonical_shas()
                lines = ["HOLDOUT_SHA256=" + hold]
                for rel in scorers:
                    lines.append("SCORER_SHA256 " + rel + "=" + scorers[rel])
                for ln in lines:
                    cmd = "printf '%s\\n' '" + ln + "' >> '" + box_log + "'"
                    ctx.exec_fn(cmd, port=ctx.port)
                stamp_ok = True
                hb("sha pins stamped into " + str(box_log) +
                   " (" + str(len(lines)) + " lines)", ctx.hb_path)
            except Exception as e:  # noqa: BLE001
                stamp_ok = False
                write_probe(ctx, "sha-stamp-failed", force=True, payload=dict(
                    err=repr(e)[:160], box_log=box_log,
                    note="leg IS dispatched; stamp evidence incomplete"))
        else:
            write_probe(ctx, "sha-stamp-failed", force=True, payload=dict(
                err="no log= in launcher stdout", stdout=stdout[:200],
                note="leg IS dispatched; leg-log path unknown"))
    harness_lib.save_json(ctx.fired_path, dict(
        rc=rc, ts=now_iso(), step=step, box_log=box_log, stamp_ok=stamp_ok,
        stdout_tail=stdout[-400:]))
    st = harness_lib.load_json(ctx.state_path) or dict()
    st["in_flight"] = None
    st["fired_rc"] = rc
    harness_lib.save_json(ctx.state_path, st)
    write_probe(ctx, "fired", force=True, payload=dict(
        rc=rc, box_log=box_log, stamp_ok=stamp_ok))
    hb("dispatch rc=" + str(rc) + " box_log=" + str(box_log) +
       " stamp_ok=" + str(stamp_ok), ctx.hb_path)
    if rc == 0:
        return 0
    return 1 if rc == 1 else 2


def load_launcher_exec():
    # The launcher module owns the real /exec contract; reuse its exec_remote
    # rather than duplicating the wire format here.
    import importlib.util
    path = str(PROJECT_ROOT / "tmp" / "c0002_launch_leg.py")
    spec = importlib.util.spec_from_file_location("c0002_launch_leg", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.exec_remote


def main(argv=None, **overrides):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff-mins", type=float, default=DEFAULT_CUTOFF_MINS)
    ap.add_argument("--port", type=int, default=HEALTH_PORT)
    args = ap.parse_args(argv)
    cutoff = now() + timedelta(minutes=args.cutoff_mins)

    def get_json(url, timeout=8):
        import urllib.request
        import json as _json
        r = urllib.request.urlopen(url, timeout=timeout)
        return _json.loads(r.read().decode("utf-8", "replace"))

    def exec_fn(cmd, wait_ms=90000, timeout=130, port=None):
        real = load_launcher_exec()
        return real(str(cmd), wait_ms=wait_ms, timeout=timeout, port=port)

    def launcher():
        return subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tmp" / "c0002_launch_leg.py"),
             "--port", str(args.port)],
            capture_output=True, text=True, timeout=900, cwd=str(PROJECT_ROOT))

    ctx = make_ctx(
        lock_path=overrides.get(
            "lock_path", str(PROJECT_ROOT / "harness/state/locks/asi2-eval.lock")),
        state_path=overrides.get(
            "state_path", str(PROJECT_ROOT / "tmp/c0051_watcher_state.json")),
        fired_path=overrides.get(
            "fired_path", str(PROJECT_ROOT / "tmp/c0051_fired.json")),
        probe_dir=overrides.get(
            "probe_dir", str(PROJECT_ROOT / "harness/state/probes")),
        c0002_fired_path=overrides.get(
            "c0002_fired_path", str(PROJECT_ROOT / "tmp/c0002_fired.json")),
        hb_path=overrides.get(
            "hb_path", str(PROJECT_ROOT / "harness/state/agents/C-0051.progress")),
        get_json=overrides.get("get_json", get_json),
        exec_fn=overrides.get("exec_fn", exec_fn),
        launcher=overrides.get("launcher", launcher),
        cutoff=overrides.get("cutoff", cutoff),
        port=overrides.get("port", args.port),
    )
    tok = arm(ctx)
    if tok is None:
        return 4
    rc = 3
    try:
        fired = False
        while now() < ctx.cutoff:
            action, reason = poll_once(ctx)
            if action == "fire":
                rc = dispatch(ctx)
                fired = True
                break
            if action == "stop":
                if getattr(ctx, "_terminal_probed", None) != reason:
                    write_probe(ctx, reason, force=True,
                                payload=dict(note="terminal no-fire, watcher stops"))
                rc = 5
                break
            time.sleep(POLL_S)
        if not fired and rc == 3:
            write_probe(ctx, "cutoff-never-ready", force=True, payload=dict(
                cutoff_utc=ctx.cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
                note="ASI2 never ready+exec-ok this window"))
    finally:
        t = getattr(ctx, "_tok", None) or tok
        if t:
            release(ctx, t)
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        hb_path = str(PROJECT_ROOT / "harness/state/agents/C-0051.progress")
        harness_lib.append_line(
            hb_path, now_iso() + " c0051-watcher crashed: " + repr(e)[:200])
        sys.exit(2)

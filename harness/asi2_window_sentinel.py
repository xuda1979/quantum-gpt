#!/usr/bin/env python3
"""C-9061: ASI2 window-open sentinel -- detect-only, bounded, fail-closed.

Re-files the DETECT half of C-0051 (combined detect+fire watcher), which
bounced 3x on "no RESULT verdict" because it waited for the eval window
inside its own budget. This sentinel is bounded: ONE pass, ONE terminal
artifact, then exit -- window_open.json when the C-9020 two-signal bar is
met, window_not_open.json (with the last probe JSON) otherwise. The FIRE
half stays with the C-9029 requeue path: on window-open this sentinel
names its consumer in the artifact and NEVER dispatches, launches, or
requeues anything itself.

Bar (C-9020 two-signal):
  1. :19004 /health 200 with body ready=true;
  2. the SAME health pid held across >= pid_gap_s (default 300s) -- the
     C-9020 boot-restart loop shows ready=true under a NEW pid every
     probe and must never certify a window;
  3. an ACTIVE /exec "echo ALIVE" round-trip (C-9021: a clean health
     body cannot distinguish ready from wedged) -- run ONLY after 1+2
     hold, so a wedged or pid-churning daemon is never loaded.

Every probe is banked under probes_dir as C-9061-poll-NN-<ts>.json. Any
probe error is fail-closed: unknown is never open.

Boundedness: poll interval POLL_S=60s (--poll-s); budget BUDGET_S=1500s
(--budget-s); the loop sleeps min(POLL_S, remaining) and ALWAYS ends with
exactly one terminal artifact. Exit 0 = DONE (artifact written, either
verdict); 2 = crash (still writes window_not_open, reason=sentinel-crash).

Supersedes: C-0051 (detect half; re-filed as this split shape).
"""

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLL_S = 60.0  # documented poll interval
BUDGET_S = 1500.0  # hard bound; never waits past this
PID_GAP_S = 300.0  # C-9020: same pid must hold >=5 min apart
PORT = 19004
ECHO_COMMAND = "echo ALIVE"
ECHO_WAIT_MS = 15000
ARTIFACT_DIR = ROOT / "harness/state/c9061"
PROBES_DIR = ROOT / "harness/state/probes"
SUPERSEDES = (
    "C-0051 (combined detect+fire watcher; detect split into this "
    "sentinel, fire stays with the C-9029 requeue path)"
)


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_ctx(
    artifact_dir,
    probes_dir,
    port=PORT,
    budget_s=BUDGET_S,
    poll_s=POLL_S,
    pid_gap_s=PID_GAP_S,
    health_fn=None,
    exec_fn=None,
    clock=time.monotonic,
    sleep=time.sleep,
):
    """All I/O and time are injected: the suite never touches the network
    and never really sleeps (C-0051's bounce mode was waiting inside its
    own budget -- injected time makes boundedness testable)."""
    return dict(
        artifact_dir=str(artifact_dir),
        probes_dir=str(probes_dir),
        port=int(port),
        budget_s=float(budget_s),
        poll_s=float(poll_s),
        pid_gap_s=float(pid_gap_s),
        health_fn=health_fn,
        exec_fn=exec_fn,
        clock=clock,
        sleep=sleep,
        polls=0,
    )


def _bank_probe(ctx, rec):
    d = Path(ctx["probes_dir"])
    d.mkdir(parents=True, exist_ok=True)
    name = "C-9061-poll-%02d-%s.json" % (rec["poll"], rec["ts"].replace(":", ""))
    path = d / name
    path.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return path


def _probe_once(ctx, baseline):
    """One poll: health probe; the active exec confirm runs ONLY once the
    health pid has been stable >= pid_gap_s. Fail-closed throughout.
    Returns (rec, baseline)."""
    now = ctx["clock"]()
    rec = dict(
        card="C-9061",
        poll=ctx["polls"],
        ts=_now_iso(),
        port=ctx["port"],
        ready=False,
        pid=None,
        pid_stable_s=None,
        exec=None,
        error=None,
        baseline_reset=False,
        bar_ready=False,
    )
    try:
        h = ctx["health_fn"](ctx["port"])
        body = json.loads(h.get("body") or "{}")
        rec["ready"] = (h.get("code") == 200) and (body.get("ready") is True)
        rec["pid"] = body.get("pid")
    except Exception as exc:  # probe failure is NOT ready (fail closed)
        rec["error"] = "health: " + repr(exc)[:200]
        return rec, None  # daemon unobservable -> stability baseline void
    if not rec["ready"]:
        return rec, None  # booting/down -> baseline void
    if baseline is None or baseline.get("pid") != rec["pid"]:
        rec["baseline_reset"] = baseline is not None  # C-9020 pid churn
        return rec, dict(pid=rec["pid"], t0=now)
    rec["pid_stable_s"] = now - baseline["t0"]
    if rec["pid_stable_s"] < ctx["pid_gap_s"]:
        return rec, baseline
    # signals 1+2 hold: NOW the active /exec echo positive control
    try:
        e = ctx["exec_fn"](ctx["port"], ECHO_COMMAND)
        out = str(e.get("output", "")) if isinstance(e, dict) else str(e)
        alive = isinstance(e, dict) and e.get("rc") == 0 and "ALIVE" in out
        rec["exec"] = "ALIVE" if alive else ("exec: " + repr(e)[:160])
    except Exception as exc:  # a wedged exec is NOT a window (fail closed)
        rec["exec"] = "exec: " + repr(exc)[:180]
    rec["bar_ready"] = rec["exec"] == "ALIVE"
    return rec, baseline


def _write_artifact(ctx, name, payload):
    d = Path(ctx["artifact_dir"])
    d.mkdir(parents=True, exist_ok=True)
    path = d / name
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    return path


def run_sentinel(ctx):
    """ONE bounded pass -> exactly one terminal artifact -> (verdict, rc)."""
    baseline = None
    last = None
    banked = []
    deadline = ctx["clock"]() + ctx["budget_s"]
    while ctx["clock"]() < deadline:
        ctx["polls"] += 1
        rec, baseline = _probe_once(ctx, baseline)
        banked.append(str(_bank_probe(ctx, rec)))
        last = rec
        if rec["bar_ready"]:
            _write_artifact(
                ctx,
                "window_open.json",
                dict(
                    card="C-9061",
                    artifact="window_open",
                    generated_utc=_now_iso(),
                    port=ctx["port"],
                    bar=dict(
                        health_ready=True,
                        pid=rec["pid"],
                        pid_stable_s=rec["pid_stable_s"],
                        exec="ALIVE",
                        pid_gap_s=ctx["pid_gap_s"],
                    ),
                    consumer=dict(
                        card="C-9029",
                        action="requeue",
                        note=(
                            "sentinel NEVER dispatches/launches/"
                            "requeues; it only writes this artifact"
                        ),
                    ),
                    supersedes=SUPERSEDES,
                    probes=banked,
                    polls=ctx["polls"],
                ),
            )
            return "window_open", 0
        remaining = deadline - ctx["clock"]()
        if remaining > 0:
            ctx["sleep"](min(ctx["poll_s"], remaining))
    _write_artifact(
        ctx,
        "window_not_open.json",
        dict(
            card="C-9061",
            artifact="window_not_open",
            generated_utc=_now_iso(),
            port=ctx["port"],
            reason="budget-exhausted-window-not-open",
            budget_s=ctx["budget_s"],
            poll_s=ctx["poll_s"],
            polls=ctx["polls"],
            last_probe=last,
            probes=banked,
            supersedes=SUPERSEDES,
        ),
    )
    return "window_not_open", 0


def live_health(port, timeout=8):
    with urllib.request.urlopen("http://127.0.0.1:%d/health" % port, timeout=timeout) as r:
        return dict(code=r.getcode(), body=r.read().decode("utf-8", "replace"))


def live_exec_echo(port, command=ECHO_COMMAND, wait_ms=ECHO_WAIT_MS):
    """Active positive control through the daemon /exec transport (wire
    shape per scripts/asi3_exec.py and C-0066: key "command", "waitMs")."""
    req = urllib.request.Request(
        "http://127.0.0.1:%d/exec" % port,
        data=json.dumps(dict(command=command, waitMs=wait_ms)).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=max(30.0, wait_ms / 1000.0 + 15.0)) as r:
        code = r.getcode()
        raw = r.read().decode("utf-8", "replace")
    try:
        body = json.loads(raw)
    except ValueError:
        body = {}
    out = body.get("output", raw)
    rc = 0 if (code == 200 and body.get("ok") and "ALIVE" in str(out)) else 1
    return dict(rc=rc, output=str(out)[:400], commandStatus=body.get("commandStatus"))


def main(argv=None, ctx_factory=None):
    ap = argparse.ArgumentParser(
        description="C-9061 ASI2 window-open sentinel (detect-only, bounded)"
    )
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--budget-s", type=float, default=BUDGET_S)
    ap.add_argument("--poll-s", type=float, default=POLL_S)
    ap.add_argument("--pid-gap-s", type=float, default=PID_GAP_S)
    ap.add_argument("--artifact-dir", default=str(ARTIFACT_DIR))
    ap.add_argument("--probes-dir", default=str(PROBES_DIR))
    args = ap.parse_args(argv)
    if ctx_factory is not None:
        ctx = ctx_factory(args)
    else:
        ctx = make_ctx(
            args.artifact_dir,
            args.probes_dir,
            port=args.port,
            budget_s=args.budget_s,
            poll_s=args.poll_s,
            pid_gap_s=args.pid_gap_s,
            health_fn=live_health,
            exec_fn=live_exec_echo,
        )
    try:
        verdict, rc = run_sentinel(ctx)
        print("c9061: %s (rc=%d) terminal artifact in %s" % (verdict, rc, ctx["artifact_dir"]))
        return rc
    except Exception as exc:  # crash must still fail closed
        try:
            _write_artifact(
                ctx,
                "window_not_open.json",
                dict(
                    card="C-9061",
                    artifact="window_not_open",
                    generated_utc=_now_iso(),
                    reason="sentinel-crash",
                    error=repr(exc)[:300],
                    polls=ctx.get("polls", 0),
                    supersedes=SUPERSEDES,
                ),
            )
        except OSError:
            pass
        print("c9061 sentinel crashed: " + repr(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

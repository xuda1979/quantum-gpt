"""Fail-closed resource probes for the QG harness (cards C-0024/C-0008 lineage).

Three-state rule (skill §5.4.1): every probe returns ALIVE ("ready") on positive
evidence only; transport death, non-200, empty output, and parse failure are all
UNKNOWN — never "dead", never absent. A resource not reported is a resource not
verified; these probes feed harness/state/probes/*.json and the standup renderer.

Production defaults: health via urllib against the box daemon port; the trainer
probe prefers an injected exec transport (box /exec) and falls back to run-dir
FILE evidence (C-0074 probe_trainer_files: eval_results.jsonl step ladder +
freshness) — with neither, the trainer is UNKNOWN, never assumed healthy.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

DAEMON_PORTS = {"asi1": 20646, "asi2": 19004, "asi3": 20653}
TRAIN_FIRE_STATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "harness",
    "state",
    "asi3_train_fire_state.json",
)
TRAINER_PS_CMD = "ps -eo pid,etimes,args | grep -E 'grpo_trainer\\.py' | grep -v grep | head -3"

# B-263 heal-detect thresholds (C-0008): /health ready=true does NOT certify
# the /exec transport. Measured 2026-09-16: ASI1/ASI3 sat ready with a stuck
# busy exec slot while the pending queue only grew; every /exec echo timed out.
WEDGE_BUSY_AGE_MS = 120_000  # busy exec slot stuck >= 2 min with no completion
WEDGE_PENDING_MIN = 25  # pending queue flood; a healthy daemon drains it
BOOT_STUCK_UPTIME_S = 420  # normal boot is ~4-5 min; still booting past this = stuck
TRAINER_FILE_STALE_S = 1800  # file evidence older than this is not positive liveness
STUB_MODEL_SIGNATURES = ("someorg/", "some-model")  # C-9019: argparse-default scaffold


def _daemon_exec(port, command, timeout=10):
    """POST a command to a box daemon /exec endpoint, return stdout text.

    Same transport contract as scripts/run_and_report.py run_box(); kept
    local so probes never import harness scripts (one-way dep). Raises on
    any transport failure — callers fail closed to UNKNOWN."""
    import json as _json
    import urllib.request

    payload = _json.dumps({"command": command}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = _json.loads(resp.read().decode("utf-8", errors="replace"))
    return str(body.get("output") or "")


def classify_transport(health):
    """Classify a parsed /health body (B-263 heal-detect, C-0008).

    /health ready=true does NOT certify the /exec transport: a daemon can sit
    ready with a permanently-stuck busy exec slot while its pending queue only
    grows (measured ASI1/ASI3 2026-09-16). Returns dict(status, evidence) with
    status in: ready | exec_wedged | boot_failed | boot_stuck | booting | unknown.
    """
    ev = dict()
    try:
        ev["startupState"] = health.get("startupState")
        ev["ready"] = bool(health.get("ready"))
        ev["uptime_s"] = health.get("uptime")
        ev["busy"] = bool(health.get("busy"))
        ev["busyAgeMs"] = health.get("busyAgeMs")
        ev["pendingRequestCount"] = health.get("pendingRequestCount")
        ev["lastCommandStartedAt"] = health.get("lastCommandStartedAt")
        ev["lastCommandCompletedAt"] = health.get("lastCommandCompletedAt")
    except AttributeError:
        return dict(status="unknown", evidence=ev)
    if ev["startupState"] == "error":
        return dict(status="boot_failed", evidence=ev)
    if ev["startupState"] == "booting":
        up = ev["uptime_s"] or 0
        stuck = up > BOOT_STUCK_UPTIME_S
        return dict(status="boot_stuck" if stuck else "booting", evidence=ev)
    if not ev["ready"]:
        return dict(status="unknown", evidence=ev)
    slot_done = ev["lastCommandCompletedAt"] is not None
    age_ok = isinstance(ev["busyAgeMs"], (int, float))
    stall = ev["busy"] and not slot_done and age_ok and ev["busyAgeMs"] >= WEDGE_BUSY_AGE_MS
    pend = ev["pendingRequestCount"]
    flood = isinstance(pend, (int, float)) and pend >= WEDGE_PENDING_MIN
    stuck = stall or flood
    if stuck:
        return dict(status="exec_wedged", evidence=ev)
    return dict(status="ready", evidence=ev)


def _default_health(port, timeout=6):
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return {"code": resp.status, "body": resp.read(65536).decode("utf-8", "replace")}
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {"code": None, "body": "", "error": str(exc)[:120]}


def _unknown(what, detail):
    return {"status": "unknown", "summary": f"UNKNOWN ({what}: {detail})"}


def probe_daemon(name, port, health_fn=None, exec_probe_fn=None):
    """Probe one box daemon. 200 + parseable body -> ready; anything else unknown.

    C-9021 two-signal verdict: /health-ready alone is NOT certification. When
    exec_probe_fn is provided, an ACTIVE exec echo round-trip must also pass;
    a clean body with a failing control renders UNKNOWN HEALTH=ready EXEC=wedged.
    """
    fn = health_fn or _default_health
    try:
        r = fn(port)
    except Exception as exc:  # probe must never raise
        return _unknown("health probe raised", str(exc)[:120])
    code = r.get("code")
    body = r.get("body") or ""
    if code != 200:
        detail = "transport error" if code is None else f"HTTP {code}"
        extra = r.get("error")
        return _unknown("health non-200", detail if not extra else f"{detail} ({extra})")
    try:
        data = json.loads(body)
        ready = bool(data.get("ready"))
        pid = data.get("pid")
    except ValueError:
        ready, pid = None, None
    if ready is None:
        return _unknown("health body unparseable", body[:60])
    if not ready:
        return {"status": "unknown", "summary": "UNKNOWN (daemon reachable, ready=false)"}
    # B-263: /health liveness does not certify /exec. A ready daemon with a
    # stuck busy exec slot renders UNKNOWN (exec_wedged), never READY.
    cls = classify_transport(data)
    # C-9021 positive control: an active exec round-trip, not just body fields.
    exec_sig = None
    if exec_probe_fn is not None:
        try:
            ctrl = exec_probe_fn(port)
            rc = ctrl.get("rc") if isinstance(ctrl, dict) else None
            exec_sig = "ok" if rc == 0 else "wedged"
        except Exception:
            exec_sig = "wedged"  # fail closed: a raising control is not a pass
    if cls["status"] == "exec_wedged":
        ev = cls["evidence"]
        summary = (
            "UNKNOWN (ready-but-exec_wedged: busyAgeMs={} pendingRequestCount={} "
            "lastCommandCompletedAt=null)"
        ).format(ev.get("busyAgeMs"), ev.get("pendingRequestCount"))
        if exec_sig:
            summary += f" EXEC={exec_sig}"
        return dict(status="unknown", transport=cls, summary=summary)
    if exec_probe_fn is not None and exec_sig != "ok":
        return dict(
            status="unknown",
            transport=cls,
            summary=(
                "UNKNOWN HEALTH=ready EXEC=wedged "
                "(active exec positive control failed; body fields alone are not certification)"
            ),
        )
    summary = f"READY /health ready=true pid={pid}" if pid else "READY /health ready=true"
    if exec_sig == "ok":
        summary = "READY HEALTH=ready EXEC=ok" + (f" pid={pid}" if pid else "")
    out = dict(status="ready", summary=summary, transport=cls)
    # positive liveness term (C-0030): the pid the daemon reported over the
    # wire; without one, the observed 200+ready=true is the positive term.
    out["liveness"] = dict(term="health_pid", pid=pid) if pid else dict(term="health_200_ready")
    return out


def probe_trainer(port, exec_fn=None):
    """Probe the ASI3 trainer via an exec transport. Positive ps evidence -> ready.

    Exec failure or EMPTY output -> UNKNOWN (an empty ps could be a transport
    truncation artifact; fail-closed never reports a confident 'no trainer').
    """
    if exec_fn is None:
        return _unknown("no exec transport configured", "trainer probe needs exec_fn")
    try:
        out = exec_fn(port, TRAINER_PS_CMD)
    except Exception as exc:
        return _unknown("exec transport died", str(exc)[:120])
    lines = [ln.strip() for ln in (out or "").splitlines() if ln.strip()]
    if not lines:
        return _unknown("ps empty (possible truncation)", "no trainer pid evidence")
    m = re.match(r"^(\d+)\s+(\d+)\s+(.*)$", lines[0])
    if not m:
        return _unknown("ps unparseable", lines[0][:80])
    pid = int(m.group(1))
    return {
        "status": "ready",
        "summary": f"READY trainer pid={pid} ({m.group(3)[:48]})",
        "liveness": {"term": "ps_pid", "pid": pid},
    }


def probe_trainer_box_aware(port, outputs_dir, now=None, proc_root=None,
                            exec_fn=None):
    """C-9590/C-0074: the trainer probe, box-aware — two evidence tiers.

    Tier 1 (box ps): a live ps on the trainer box via exec transport; a
    parseable pid row is the strongest liveness (process running NOW).
    Tier 2 (files): probe_trainer_files evidence — step ladder + freshness
    + /proc state — which works when exec is wedged or unavailable (the
    measured 2026-09-21 state: a healthy trainer invisible to a wedged
    /exec). File evidence only DOWNGRADES the verdict (a live ps never
    loses to a stale file; a ready file never loses to a missing ps) —
    the never-lie rule: exec silence must not read as 'no trainer'.

    Returns the tier-1 dict when ps evidence exists, else the tier-2 dict.
    Never raises — every failure path returns an explicit UNKNOWN with a
    named reason.

    exec_fn=None (the default) DISABLES tier 1 — callers that want box-ps
    evidence must pass a transport explicitly. This keeps unit tests
    (file-evidence fixtures, no live daemon) hermetic: a test env never
    probes a real box and picks up an unrelated live trainer.
    """
    # Tier 1: box ps via exec (only when a transport is supplied).
    if exec_fn is None:
        ps = _unknown("no exec transport configured", "box-aware tier-1 skipped")
    else:
        try:
            ps = probe_trainer(port, exec_fn=exec_fn)
        except Exception as exc:  # a transport crash must never kill the probe
            ps = _unknown("exec transport died", str(exc)[:120])
    if ps.get("status") == "ready":
        return ps
    # Tier 2: file evidence (works with zero transport).
    files = probe_trainer_files(outputs_dir, now=now, proc_root=proc_root)
    if files.get("status") == "ready":
        # Keep the tier-1 silence as a disclosed footnote, never a veto.
        files = dict(files)
        files["box_ps_note"] = str(ps.get("summary") or "")[:120]
        return files
    # Neither tier has positive evidence: return the MORE INFORMATIVE
    # unknown (files names step+age or an explicit UNMEASURABLE reason).
    files = dict(files)
    files["box_ps_note"] = str(ps.get("summary") or "")[:120]
    return files


def _is_stub_run_dir(d):
    """C-9019: a dir carrying the trainer argparse defaults (placeholder
    model_name, device != npu) in launch_config.json is a dead dry-run
    scaffold. Box-synced dirs carry no launch_config.json — never stubs.

    Returns (is_stub, reason) — the reason names the leg(s) that fired."""
    cfg_path = os.path.join(d, "launch_config.json")
    if not os.path.isfile(cfg_path):
        return False, None
    try:
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return False, None
    model = str(cfg.get("model_name") or "").lower()
    device = str(cfg.get("device") or "").lower()
    legs = []
    if device and device != "npu":
        legs.append(f"device={device}")
    if any(s in model for s in STUB_MODEL_SIGNATURES):
        legs.append(f"model={cfg.get('model_name')}")
    if legs:
        return True, ", ".join(legs)
    return False, None


def _read_step_ladder(run_dir):
    """Last parseable step from eval_results.jsonl (B-222: the ladder head)."""
    path = os.path.join(run_dir, "eval_results.jsonl")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None
    step = None
    for ln in lines:
        try:
            row = json.loads(ln)
        except ValueError:
            continue
        if isinstance(row.get("step"), int):
            step = row["step"]  # keep the LAST parseable row
    return step


def _proc_scan(proc_root, run_dir):
    """Scan <proc_root>/<pid> for a grpo_trainer.py bound to run_dir.

    Returns (live_pid, live_state, zombie_pid) — a LIVE match always wins over
    a zombie (state Z), so a shared pid across proc roots cannot shadow it."""
    live_pid = live_state = zombie_pid = None
    try:
        entries = os.listdir(proc_root)
    except OSError:
        return None, None, None
    for name in entries:
        if not name.isdigit():
            continue
        pdir = os.path.join(proc_root, name)
        try:
            with open(os.path.join(pdir, "cmdline"), encoding="utf-8") as f:
                parts = f.read().split(chr(0))
            if not any(p.endswith("grpo_trainer.py") for p in parts):
                continue
            if run_dir not in parts:
                continue
                continue
            with open(os.path.join(pdir, "stat"), encoding="utf-8") as f:
                state = f.read().split()[2]
        except (OSError, IndexError):
            continue
        if state == "Z":
            zombie_pid = int(name)
        else:
            live_pid, live_state = int(name), state
    return live_pid, live_state, zombie_pid


def probe_trainer_files(outputs_dir, now=None, proc_root=None):
    """C-0074: the trainer probe WITHOUT an exec transport.

    File evidence only: the live run dir is resolved from outputs_dir (newest
    mtime, at read time, run dirs only), the step ladder comes from
    eval_results.jsonl's `step` field (the train log is a buffering artifact,
    B-222), and liveness comes from /proc stat state when the host has it,
    else file freshness (stale past TRAINER_FILE_STALE_S is not positive).
    C-9019: a stub scaffold (argparse-default launch_config) is quarantined —
    skipped and disclosed — so it can never mask the real run dir. Never bare
    UNKNOWN: step+age, or an explicit UNMEASURABLE reason."""
    if now is None:
        import time

        now = int(time.time())
    try:
        entries = os.listdir(outputs_dir)
    except OSError:
        return dict(
            status="unknown",
            summary=f"UNMEASURABLE outputs dir unreadable: {outputs_dir}",
        )
    stubs = []
    candidates = []
    for name in entries:
        d = os.path.join(outputs_dir, name)
        if not os.path.isdir(d):
            continue  # a newer top-level FILE must not win: run dirs only
        is_stub, why = _is_stub_run_dir(d)
        if is_stub:
            stubs.append(f"{name} ({why})")
        else:
            candidates.append((os.path.getmtime(d), d, name))
    candidates.sort(reverse=True)  # newest first, resolved at read time
    run_dir = None
    step = None
    for _mtime, d, _name in candidates:
        step = _read_step_ladder(d)
        if step is not None:
            run_dir = d
            break
    disclosure = f" (skipped stub: {'; '.join(stubs)})" if stubs else ""
    if run_dir is None:
        if stubs and not candidates:
            return dict(
                status="stub",
                summary=(
                    f"STUB newest run dir is a placeholder scaffold: {stubs[0]}; "
                    f"no real evidence under {outputs_dir}"
                ),
            )
        return dict(
            status="unknown",
            summary=(
                f"UNMEASURABLE no run dir with eval_results.jsonl under {outputs_dir}{disclosure}"
            ),
        )
    try:
        age_s = int(now - os.path.getmtime(os.path.join(run_dir, "eval_results.jsonl")))
    except OSError:
        age_s = -1
    base = f"step={step} age={age_s}s run={os.path.basename(run_dir)}"
    live_pid, live_state, zombie_pid = None, None, None
    if proc_root:
        live_pid, live_state, zombie_pid = _proc_scan(proc_root, run_dir)
    if live_pid is not None:
        return dict(
            status="ready",
            summary=f"READY {base} term=proc_pid pid={live_pid}{disclosure}",
            step=step,
            age_s=age_s,
            run_dir=run_dir,
            liveness=dict(term="proc_pid", pid=live_pid, state=live_state),
        )
    if zombie_pid is not None:
        return dict(
            status="unknown",
            summary=f"UNKNOWN {base} trainer pid={zombie_pid} zombie (state Z){disclosure}",
            step=step,
            age_s=age_s,
            run_dir=run_dir,
            liveness=dict(term="proc_pid", pid=zombie_pid, state="Z"),
        )
    if 0 <= age_s <= TRAINER_FILE_STALE_S:
        return dict(
            status="ready",
            summary=f"READY {base} term=eval_results_age{disclosure}",
            step=step,
            age_s=age_s,
            run_dir=run_dir,
            liveness=dict(term="eval_results_age"),
        )
    return dict(
        status="unknown",
        summary=f"UNKNOWN {base} stale >{TRAINER_FILE_STALE_S}s{disclosure}",
        step=step,
        age_s=age_s,
        run_dir=run_dir,
        liveness=dict(term="eval_results_age"),
    )


def probe_train_fire(state_path=None, now=None, pid_alive_fn=None):
    """C-9080: standup resource line for the ASI3 train-fire window state.

    An expired or zombie-tagged state NEVER reads armed (loud, fail-closed):
    the watcher is a foreground poller, so fired=false with a past cutoff
    means no one will ever fire. Inject pid_alive_fn in tests; default is the
    real harness_lib.pid_alive."""
    import asi3_train_fire_on_ready as w
    from harness_lib import pid_alive

    if pid_alive_fn is None:
        pid_alive_fn = pid_alive
    path = state_path or TRAIN_FIRE_STATE
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        return dict(status="ABSENT", summary="ABSENT no state file (watcher never armed)")
    verdict = w.expiry_status(st, now=now)
    summary = f"{verdict} cutoff={st.get('cutoff')} fired={st.get('fired')} cycle={st.get('cycle')}"
    if verdict in ("ARMED", "EXPIRED"):
        if pid_alive_fn(st.get("pid")) is False:
            summary += f" pid={st.get('pid')} DEAD no-live-consumer"
    if verdict == "ZOMBIE":
        summary += f" reason={st.get('zombie_reason', 'unspecified')}"
    return dict(status=verdict, summary=summary)


def _default_outputs_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")


def run_all(
    state_dir,
    health_fn=None,
    trainer_exec=None,
    now=None,
    train_fire_state_path=None,
    outputs_dir=None,
    exec_probe_fn=None,
):
    """Probe every provisioned resource, write probes/<name>.json, return payloads.

    Durable-state contract: each file carries ts, status, summary; the standup
    renderer (qgh._probe_results) reads exactly these. C-9021: exec_probe_fn is
    the active positive control passed to every daemon port. C-0074: the
    trainer exec probe falls back to run-dir file evidence (outputs_dir,
    default <repo>/outputs) whenever the transport is absent or not ready.
    """
    from harness_lib import now_iso, save_json

    payloads = dict()
    for name, port in DAEMON_PORTS.items():
        payloads[name] = probe_daemon(name, port, health_fn=health_fn, exec_probe_fn=exec_probe_fn)
    t = probe_trainer(DAEMON_PORTS["asi3"], exec_fn=trainer_exec)
    if t.get("status") != "ready":
        fp = probe_trainer_files(
            outputs_dir if outputs_dir is not None else _default_outputs_dir(),
            now=now if isinstance(now, int) else None,
        )
        if "step" in fp:
            t = fp  # a real measurement beats an honest transport UNKNOWN
    payloads["trainer"] = t
    payloads["train_fire"] = probe_train_fire(state_path=train_fire_state_path)
    out_dir = os.path.join(state_dir, "probes")
    os.makedirs(out_dir, exist_ok=True)
    for name, p in payloads.items():
        rec = {"ts": now or now_iso(), "status": p.get("status"), "summary": p.get("summary")}
        if "liveness" in p:
            rec["liveness"] = p["liveness"]
        save_json(os.path.join(out_dir, f"{name}.json"), rec)
    return payloads


def box_exec(port, cmd, timeout=90):
    """Real exec transport: POST to the box daemon /exec API (body key: command)."""
    payload = json.dumps(dict(command=cmd)).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers=dict([("Content-Type", "application/json")]),
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        d = json.loads(resp.read().decode("utf-8", "replace"))
    out = d.get("output", d)
    if isinstance(out, dict):
        out = out.get("output", "")
    return str(out)


def _default_exec_post(port, payload, timeout):
    """POST helper for probe_exec_echo; returns (status, body) for classification."""
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers=dict([("Content-Type", "application/json")]),
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return dict(status=resp.status, body=resp.read(65536).decode("utf-8", "replace"))


def probe_exec_echo(port, post_fn=None, timeout=10, marker=None):
    """The C-0008/B-263 acceptance instrument: POST `echo <marker>` and require
    the marker back within `timeout` seconds.

    rc=0 only on a verified roundtrip (unique marker echoed back). A timeout is
    UNKNOWN (rc=1) — never "dead"; a wrong output is FAIL (rc=1). Every call
    generates a fresh marker so a wedged daemon replaying a cached echo cannot
    pass the second probe.
    """
    import time
    import uuid

    marker = marker or (f"ECHO_{uuid.uuid4().hex[:12].upper()}")
    fn = post_fn or _default_exec_post
    payload = json.dumps(dict(command="echo " + marker)).encode()
    t0 = time.monotonic()
    try:
        r = fn(port, payload, timeout)
        elapsed = time.monotonic() - t0
        body = r.get("body", "") if isinstance(r, dict) else str(r)
        try:
            d = json.loads(body)
            out = d.get("output", d)
            if isinstance(out, dict):
                out = out.get("output", "")
        except ValueError:
            out = body
        out = str(out).strip()
        if marker in out:
            return dict(
                rc=0,
                marker=marker,
                output=out,
                elapsed_s=round(elapsed, 3),
                summary=f"OK echo roundtrip {elapsed:.2f}s marker={marker}",
            )
        return dict(
            rc=1,
            marker=marker,
            output=out,
            elapsed_s=round(elapsed, 3),
            summary=f"FAIL marker missing from output within {timeout:.1f}s",
        )
    except Exception as exc:
        elapsed = time.monotonic() - t0
        return dict(
            rc=1,
            marker=marker,
            elapsed_s=round(elapsed, 3),
            summary=f"UNKNOWN (exec echo transport: {str(exc)[:100]})",
        )


if __name__ == "__main__":
    # CLI runner so any tick/agent can refresh the standup RESOURCES probes:
    #   /usr/bin/python3 harness/resource_probes.py
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.environ.get("QGH_STATE_DIR") or os.path.join(repo, "harness", "state")
    payloads = run_all(
        state,
        trainer_exec=box_exec,
        exec_probe_fn=probe_exec_echo,
    )
    for name in sorted(payloads):
        p = payloads[name]
        print("{} {} {}".format(name, p.get("status"), p.get("summary")))

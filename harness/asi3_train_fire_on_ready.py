#!/usr/bin/env python3
"""C-0066: ASI3 LoRA-v2 train fire-on-ready watcher (training sibling of C-0051).

Polls ASI3 (:20653) for daemon readiness AND a passing /exec echo round-trip;
the moment BOTH hold it fires the C-0039-preflighted LoRA-v2 relaunch
(scripts/qg_launch_lora_sft_fencefree_v2.sh, executed ON ASI3 through the
/exec transport) EXACTLY ONCE per armed window, under the dedicated lock
harness/state/locks/asi3-train.lock taken via harness_lib.acquire_lock.

Fail-closed contract:
  - ready=false OR exec-dead -> NO fire; a single named probe record
    harness/state/probes/C-0066-asi3-train-fire-probe.json is updated in
    place (never one record per poll -> no retry storm).
  - lock refused -> NO fire (probe record reason=lock_refused).
  - idempotent across worker restarts: pid+cutoff state file at
    harness/state/asi3_train_fire_state.json; a fired state file blocks any
    duplicate dispatch until an EXPLICIT rearm() opens a new window.
  - post-fire liveness = eval_results.jsonl "step" field advancing (B-222),
    never stdout or ps; stale-code check = pid lstart vs file mtimes (B-223).
  - coordinates with C-0051 via SEPARATE locks (asi3-train.lock, never
    asi2-eval.lock), so both may fire on the same cure event.

Exit: 0 fired; 3 cutoff reached, transport never became ready; 4 already
fired (idempotent no-op); 1 lock refused; 2 unexpected error.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
import harness_lib  # noqa: E402

LOCK_PATH = ROOT / "harness/state/locks/asi3-train.lock"
STATE_PATH = ROOT / "harness/state/asi3_train_fire_state.json"
PROBES_DIR = ROOT / "harness/state/probes"
PROBE_RECORD = "C-0066-asi3-train-fire-probe.json"
LAUNCHER_REL = "scripts/qg_launch_lora_sft_fencefree_v2.sh"
REMOTE_ROOT = "/root/work/quantum-gpt"
ASI3_PORT = 20653
POLL_S = 60
# B-223: files whose box-side mtime must predate the trainer pid lstart
STALE_CODE_FILES = [
    "training/qwen_sft_peft.py",
    "scripts/qg_launch_lora_sft_fencefree_v2.sh",
    "configs/sft/qwen38_fencefree_v2_lora.json",
]


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_or_init_state(state_path, pid, cutoff_iso):
    """Load the pid+cutoff state file; create it only when absent/corrupt.

    A reload NEVER clobbers a fired flag -- that is the duplicate-fire guard
    across worker restarts."""
    p = Path(state_path)
    if p.is_file():
        try:
            st = json.loads(p.read_text())
            if isinstance(st, dict) and "fired" in st:
                return st
        except (OSError, ValueError):
            pass
    st = dict(pid=pid, started_utc=_now(), cutoff=cutoff_iso, fired=False, cycle=1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=1) + "\n")
    return st


def rearm(state_path, pid, cutoff_iso=None):
    """Explicitly open a NEW armed window (cycle+1, fired=False).

    C-9080: stamps the new window cutoff (fail-closed loudness -- without a
    fresh stamp the window stays EXPIRED by expiry_status, never ARMED) and
    clears any zombie tag."""
    p = Path(state_path)
    try:
        st = json.loads(p.read_text())
        if not isinstance(st, dict):
            st = {}
    except (OSError, ValueError):
        st = {}
    st["fired"] = False
    st["pid"] = pid
    for k in ("zombie", "zombie_reason"):
        st.pop(k, None)  # C-9080: a re-armed window is not a zombie
    st["rearmed_utc"] = _now()
    if cutoff_iso:
        st["cutoff"] = cutoff_iso
    st["cycle"] = int(st.get("cycle", 0)) + 1
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=1) + "\n")
    return st


def cleanup_zombie(state_path, new_cutoff, now=None, pid_alive_fn=None):
    """C-9164: Clean up a zombie-tagged train-fire state file.

    Verifies the old pid is dead (fail-closed: if pid_alive_fn returns True,
    the zombie tag is PRESERVED and the state is returned unchanged).

    On success:
      - Removes zombie / zombie_reason keys.
      - Sets fired=False with the new cutoff window.
      - Increments cycle (prior cycle is marked complete).
      - Stamps prior_cycle_complete=True and cleaned_utc.
      - Writes the cleaned state back to disk.

    Returns the cleaned state dict (or the original zombie state if pid
    was still alive).
    """
    p = Path(state_path)
    try:
        st = json.loads(p.read_text())
        if not isinstance(st, dict):
            st = {}
    except (OSError, ValueError):
        st = {}

    # Fail-closed: if the old pid is still alive, do NOT clear zombie
    if pid_alive_fn is not None:
        old_pid = st.get("pid")
        if old_pid is not None and pid_alive_fn(old_pid):
            # Zombie is real -- keep the tag, return unchanged
            return st

    # Record prior cycle as complete
    prior_cycle = int(st.get("cycle", 0))
    st["prior_cycle_complete"] = True
    st["prior_cycle"] = prior_cycle

    # Clear zombie tags
    for k in ("zombie", "zombie_reason", "rearm_owner", "rearm_gate"):
        st.pop(k, None)

    # Fresh armed window
    st["fired"] = False
    st["cutoff"] = new_cutoff
    st["cycle"] = prior_cycle + 1
    st["cleaned_utc"] = _now()

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=1) + "\n")
    return st


def expiry_status(state, now=None):
    """C-9080: classify an armed-looking state file against wall time.

    Fail-closed loudness: an expired cutoff (or a zombie-tagged file, or an
    unparseable cutoff) is NEVER "ARMED" -- the watcher is a foreground
    poller, so an old fired=false file is a zombie artifact, not a live
    window. Returns ARMED / EXPIRED / FIRED / ZOMBIE / UNKNOWN.
    """
    if state.get("zombie"):
        return "ZOMBIE"
    if state.get("fired"):
        return "FIRED"
    try:
        cutoff = datetime.strptime(state.get("cutoff"), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except (TypeError, ValueError):
        return "UNKNOWN"
    if now is None:
        now = datetime.now(timezone.utc)
    return "ARMED" if now < cutoff else "EXPIRED"


def write_probe_record(probes_dir, reason, detail=None):
    """Fail-closed NOFIRE/LOCK_REFUSED evidence: ONE named record, updated in
    place with a poll counter -- repeated dead polls never spam probes/."""
    d = Path(probes_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / PROBE_RECORD
    try:
        prev = json.loads(path.read_text())
        if not isinstance(prev, dict):
            prev = {}
    except (OSError, ValueError):
        prev = {}
    rec = dict(
        card="C-0066",
        generated_utc=_now(),
        fired=False,
        reason=reason,
        polls=int(prev.get("polls", 0)) + 1,
    )
    if detail:
        rec["detail"] = detail
    path.write_text(json.dumps(rec, indent=1) + "\n")
    return path


def fire_command(remote_root=REMOTE_ROOT, launcher_rel=LAUNCHER_REL):
    """The single remote command: run the C-0039-preflighted launcher ON ASI3."""
    return f"cd {remote_root} && nohup bash {launcher_rel} >> logs/qg-lora-v2-relaunch.log 2>&1 & echo LAUNCHED $!"


def maybe_fire(state, state_path, lock_path, probes_dir, dispatch, ready, exec_ok, pid=None):
    """Core decision. Returns (verdict, info); verdict in
    FIRED / NOFIRE / ALREADY_FIRED / LOCK_REFUSED."""
    if state.get("fired"):
        return "ALREADY_FIRED", dict(dispatched=False)
    if not ready:
        write_probe_record(probes_dir, "not_ready", dict(ready=bool(ready), exec_ok=bool(exec_ok)))
        return "NOFIRE", dict(dispatched=False)
    if not exec_ok:
        write_probe_record(probes_dir, "exec_dead", dict(ready=bool(ready), exec_ok=bool(exec_ok)))
        return "NOFIRE", dict(dispatched=False)
    token = harness_lib.acquire_lock(str(lock_path))
    if token is None:
        write_probe_record(probes_dir, "lock_refused", dict(ready=True, exec_ok=True))
        return "LOCK_REFUSED", dict(dispatched=False, lock_token=None)
    try:
        cmd = fire_command()
        out = dispatch(cmd)
        state["fired"] = True
        state["fired_utc"] = _now()
        state["fired_pid"] = pid if pid is not None else os.getpid()
        state["dispatch_rc"] = out.get("rc") if isinstance(out, dict) else None
        state["fire_command"] = cmd
        harness_lib.save_json(str(state_path), state)
        return "FIRED", dict(dispatched=True, lock_token=token, dispatch=out)
    except Exception as exc:  # noqa: BLE001 -- fail closed, never mark fired
        write_probe_record(probes_dir, "dispatch_error", dict(err=repr(exc)[:200]))
        return "NOFIRE", dict(dispatched=False, error=repr(exc)[:200])
    finally:
        harness_lib.release_lock(str(lock_path), token)


def eval_step(run_dir):
    """B-222: last "step" in eval_results.jsonl -- the ONLY liveness signal.
    Missing/unreadable -> None (unmeasured), never 0."""
    p = Path(run_dir) / "eval_results.jsonl"
    if not p.is_file():
        return None
    step = None
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            s = rec.get("step")
            if isinstance(s, (int, float)):
                step = int(s)
    return step


def liveness_advancing(run_dir, prev_step):
    """True iff the B-222 step field advanced past prev_step; None when either
    side is unmeasured (fail closed: never claim liveness without evidence)."""
    cur = eval_step(run_dir)
    if cur is None or prev_step is None:
        return None
    return cur > prev_step


def stale_code_record(lstart_epoch, file_mtimes):
    """B-223: a box edit AFTER the trainer pid lstart is NOT loaded code."""
    newer = sorted(rel for rel, m in file_mtimes.items() if m > lstart_epoch)
    return dict(
        stale=bool(newer),
        lstart_epoch=lstart_epoch,
        newer_than_process=newer,
        checked=sorted(file_mtimes.keys()),
    )


def stale_code_probe_command(remote_root=REMOTE_ROOT):
    """Box-side one-liner yielding epoch mtime + name for STALE_CODE_FILES
    (the pid lstart is read separately via: ps -o lstart= -p $TRAINER_PID)."""
    stats = " ".join(f"{remote_root}/{rel}" for rel in STALE_CODE_FILES)
    return "stat -c '%Y %n' " + stats


def live_probes(port=ASI3_PORT):
    """Production probe pair: daemon readiness + /exec echo round-trip.
    Reuses scripts/exec_heal_probe.py (C-0008/B-263, field-proven)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import exec_heal_probe as ehp  # noqa: E402

    h = ehp.health_probe(port)
    e = ehp.exec_roundtrip(port)
    return bool(h.get("ready")), e.get("echo_ok") is True


def dispatch_via_exec(command, port=ASI3_PORT, wait_ms=30000):
    """Production fire: POST the launch command through the ASI3 /exec
    transport (wire shape per scripts/asi3_exec.py: key "command", "waitMs")."""
    req = urllib.request.Request(
        "http://127.0.0.1:%d/exec" % port,
        data=json.dumps({"command": command, "waitMs": wait_ms}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=max(60, wait_ms / 1000 + 30)) as resp:
        result = json.load(resp)
    ok = bool(result.get("ok")) and result.get("commandOk") is not False
    return dict(
        rc=0 if ok else 1,
        stdout=str(result.get("output", ""))[:400],
        commandStatus=result.get("commandStatus"),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="C-0066 ASI3 train fire-on-ready watcher")
    ap.add_argument("--port", type=int, default=ASI3_PORT)
    ap.add_argument("--cutoff", default="23:59", help="UTC HH:MM end of this window")
    ap.add_argument("--interval", type=int, default=POLL_S)
    ap.add_argument("--state", default=str(STATE_PATH))
    ap.add_argument("--lock", default=str(LOCK_PATH))
    ap.add_argument("--probes-dir", default=str(PROBES_DIR))
    ap.add_argument(
        "--run-dir", default=None, help="post-fire: watch this run dir eval_results.jsonl (B-222)"
    )
    ap.add_argument(
        "--rearm", action="store_true", help="explicitly open a new window (clears a fired flag)"
    )
    ap.add_argument("--once", action="store_true", help="single probe, no loop")
    args = ap.parse_args(argv)

    hb = ROOT / "harness/state/agents/C-0066.progress"
    hh, mm = args.cutoff.split(":")
    day = datetime.now(timezone.utc)
    cutoff = day.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    if cutoff < day:
        cutoff = cutoff.replace(day=day.day)  # same-UTC-day window

    def log(msg):
        line = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + " c0066: " + msg + "\n"
        try:
            with open(hb, "a") as f:
                f.write(line)
        except OSError:
            pass
        print(line, end="", flush=True)

    if args.rearm:
        rearm(args.state, os.getpid(), cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
        log("rearmed: new window opened")
    st = load_or_init_state(args.state, os.getpid(), cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"))
    if st.get("fired"):
        log("state fired at {}; no duplicate fire (restart-idempotent)".format(st.get("fired_utc")))
        return 4

    def dispatch(command):
        return dispatch_via_exec(command, port=args.port)

    polls = 0
    while datetime.now(timezone.utc) < cutoff:
        polls += 1
        try:
            ready, exec_ok = live_probes(args.port)
        except Exception as exc:  # noqa: BLE001 -- probe failure is NOT ready
            ready, exec_ok = False, False
            log("probe error (fail-closed): " + repr(exc)[:120])
        verdict, info = maybe_fire(
            state=st,
            state_path=args.state,
            lock_path=args.lock,
            probes_dir=args.probes_dir,
            dispatch=dispatch,
            ready=ready,
            exec_ok=exec_ok,
        )
        if verdict == "FIRED":
            log("FIRED relaunch (poll %d): %s" % (polls, str(info.get("dispatch"))[:150]))
            if args.run_dir:
                prev = eval_step(args.run_dir)
                for _ in range(30):
                    time.sleep(max(args.interval, 30))
                    adv = liveness_advancing(args.run_dir, prev)
                    if adv is True:
                        log("liveness confirmed: eval_results step advanced (B-222)")
                        break
                    log(f"liveness poll: step={eval_step(args.run_dir)!r} advancing={adv!r}")
            return 0
        if verdict == "LOCK_REFUSED":
            log("asi3-train.lock held elsewhere; no fire this window")
            return 1
        if polls % 5 == 1:
            log(
                "poll %d: ready=%s exec_ok=%s -> NOFIRE (probe record updated)"
                % (polls, ready, exec_ok)
            )
        if args.once:
            return 3
        time.sleep(args.interval)
    log("cutoff reached; transport never became ready this window")
    return 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print("c0066 watcher crashed: " + repr(e)[:200], file=sys.stderr)
        sys.exit(2)

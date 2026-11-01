#!/usr/bin/env python3
"""C-10610 battery reconciler — the ONE host-side supervisor for the IBM
Qiskit HumanEval baseline battery on ASI2.

Doctrine (daemon_reconciler.py): exactly ONE remedy per failure class,
absorb transport fragility, never kill a healthy process.

Observed failure classes (2026-10-30/31 incidents):
  A. container restart     -> inner battery killed, journals survive
                              -> remedy: re-dispatch via c10610_ibm_baseline_dispatch.py
                                 --skip-wait (idempotent, journal-resuming)
  B. env wipe              -> pip packages live in the ephemeral container layer;
                              restart wipes them; c10609 exits instantly
                              ("qiskit runtime missing on box")
                              -> remedy: pip3 install the authority pins, then
                                 re-dispatch (class A remedy)
  C. transport flap        -> run_box FAIL/BOX_DOWN; NOT a battery failure
                              -> remedy: none (just retry next cycle)

Cycle (default 300s):
  1. probe box (echo). DOWN -> class C, next cycle.
  2. battery alive (pgrep c10610_battery_inner.sh or c10609 eval)? yes -> log poll.
  3. DONE marker? -> battery_complete, exit 0.
  4. box up + battery gone + no DONE -> check qiskit importable:
     - missing -> class B: pip install env, then re-dispatch (class A).
     - present -> class A: re-dispatch directly.
  Re-dispatch rate-limited to once per RELAUNCH_COOLDOWN_S (a dispatch that
  dies within the cooldown still gets ONE immediate env-fix retry path via
  the qiskit-import check ordering above; beyond that, cooldown wins).

Fail-closed: exits nonzero only after MAX_H without DONE marker.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from run_and_report import run_box  # noqa: E402

BOX = "ASI2"
BOX_ROOT = "/root/work/quantum-gpt"
OUT_BOX = BOX_ROOT + "/outputs/ibm_baseline_c10610"
LOG = REPO / "logs" / "c10610_battery_reconciler.log"
CYCLE_S = 300
RELAUNCH_COOLDOWN_S = 180  # a dispatch + instant-die must not tight-loop
MAX_H = 96

# authority: requirements-cpu-eval.txt pins; plus the box-env items named in
# the C-10610 journal (matplotlib/networkx/pylatexenc/qiskit-ibm-runtime)
PIP_SPEC = '"qiskit>=1.2,<3.0" "qiskit-aer>=0.14" pylatexenc matplotlib networkx qiskit-ibm-runtime'

PROBE_CMD = "echo RECON_ALIVE"
STATE_CMD = (
    f"OUT={OUT_BOX}; "
    "D=0; [ -f $OUT/DONE ] && D=1; "
    "A=0; pgrep -f c10610_battery_inner >/dev/null && A=1; "
    "E=0; pgrep -f c10609_ibm_qiskit_humaneval_eval >/dev/null && E=1; "
    "Q=0; python3 -c 'import qiskit, qiskit_aer, pylatexenc, matplotlib, networkx' 2>/dev/null && Q=1; "
    "T=0; [ -f $OUT/battery.log ] && T=$(grep -c task_done $OUT/battery.log); "
    f'echo "$D $A $E $Q $T"'
)


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def emit(stage: str, **kw) -> None:
    line = json.dumps(dict(ts_utc=now_utc(), stage=stage, **kw), ensure_ascii=False)
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def probe() -> str:
    r = run_box(BOX, PROBE_CMD, timeout=30)
    return "UP" if r.get("status") == "PASS" else "DOWN"


def state() -> dict | None:
    r = run_box(BOX, STATE_CMD, timeout=60)
    if r.get("status") != "PASS":
        return None
    m = re.search(r"^([01]) ([01]) ([01]) ([01]) (\d+)$", (r.get("stdout") or "").strip(), re.M)
    if not m:
        return None
    d, a, e, q, t = (int(x) for x in m.groups())
    return dict(done=bool(d), inner_alive=bool(a), eval_alive=bool(e), env_ok=bool(q), tasks=t)


def provision_env() -> bool:
    cmd = (
        f"pip3 install -q {PIP_SPEC} 2>&1 | grep -E 'ERROR|Successfully' | tail -n 3; "
        "python3 -c 'import qiskit, qiskit_aer, pylatexenc, matplotlib, networkx' "
        "&& echo ENV_RESTORED"
    )
    for _ in range(3):
        r = run_box(BOX, cmd, timeout=580)
        if r.get("status") == "PASS" and "ENV_RESTORED" in (r.get("stdout") or ""):
            return True
        time.sleep(45)
    return False


def redispatch() -> bool:
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "harness" / "scripts" / "c10610_ibm_baseline_dispatch.py"),
            "--skip-wait",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=900,
    )
    out = (r.stdout or "") + (r.stderr or "")
    ok = "battery_dispatched" in out
    emit(
        "redispatch",
        ok=ok,
        rc=r.returncode,
        detail=out.strip().splitlines()[-1][:160] if out.strip() else "",
    )
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-h", type=float, default=MAX_H)
    args = ap.parse_args()
    emit("reconciler_start", box=BOX, cycle_s=CYCLE_S, max_h=args.max_h)
    deadline = time.time() + args.max_h * 3600
    last_dispatch = 0.0
    down_streak = 0
    while time.time() < deadline:
        if probe() != "UP":
            down_streak += 1
            emit("box_down", streak=down_streak)
            time.sleep(CYCLE_S)
            continue
        down_streak = 0
        s = state()
        if s is None:
            emit("state_unreadable")  # flap mid-cycle; not a battery event
            time.sleep(CYCLE_S)
            continue
        emit("cycle", **s)
        if s["done"]:
            emit("battery_complete")
            return 0
        if s["inner_alive"] or s["eval_alive"]:
            time.sleep(CYCLE_S)  # healthy; no remedy
            continue
        # battery gone, box up, not done -> class A (with B pre-check)
        if time.time() - last_dispatch < RELAUNCH_COOLDOWN_S:
            emit("cooldown_hold")
            time.sleep(CYCLE_S)
            continue
        if not s["env_ok"]:
            emit("env_wiped_provisioning")
            if not provision_env():
                emit("env_provision_failed")
                time.sleep(CYCLE_S)
                continue
            emit("env_restored")
        last_dispatch = time.time()
        if redispatch():
            emit("battery_relaunched")
        time.sleep(CYCLE_S)
    emit("reconciler_timeout_no_done")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

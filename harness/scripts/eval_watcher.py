#!/usr/bin/env python3
"""eval_watcher.py — ASI2-side standing eval loop, decoupled from the trainer box.

Runs ON ASI2 (installed there once; NAS is local there). Polls the NAS
checkpoint bus /root/work/ckpt_bus (shared with ASI3). For each NEW checkpoint
(manifest.json present, no verdict.json yet):
  1. copy adapter to box-local /vllm-workspace/eval_adapters/{run}/{step}
  2. run the fail-closed 18-task leg (3 parallel slices) via the proven
     scripts/run_holdout_leg1.py mechanism, in the /root/work/software checkout
     (never ASI3; never through the daemon — NAS + local disk only)
  3. write verdict.json back to the bus step dir

The Mac side installs/starts it (install_eval_watcher.py) and only reads state:
harness/state/eval_watcher.json is synced back over NAS.

Usage (ON ASI2):
    python3 eval_watcher.py --once
    nohup python3 eval_watcher.py --loop &        # 60s poll, survives restarts
    python3 eval_watcher.py --status
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_config import get  # noqa: E402

BUS = Path(get("ckpt_bus.nas_root"))
EVAL_REPO = Path(get("box.eval_repo"))          # /root/work/software/quantum-gpt
EVAL_ADAPTERS = Path(get("box.eval_adapters_dir"))
STATE = BUS / "eval_watcher_state.json"          # lives on NAS: Mac reads it too
POLL_S = 60

# Verdict from envelope + merged scores; fail-closed marker rule from contracts.
VERDICT_PY = r'''
import json, sys
env_p, scores_p, out_p, man_p = sys.argv[1:5]
e = json.load(open(env_p))
m = json.load(open(man_p))
s = json.load(open(scores_p))
recs = s.get("records", [])
def passes(model):
    rows = [r for r in recs if r.get("model") == model]
    return {"passed": sum(1 for r in rows if r.get("passed")), "total": len(rows)}
ok = bool(e.get("adapter_applied_marker")) and bool(e.get("adapter_probe_differs_marker"))
v = {
    "status": "OK" if ok else "VOID",
    "fail_closed": {
        "adapter_applied": e.get("adapter_applied_marker"),
        "probe_differs": e.get("adapter_probe_differs_marker"),
    },
    "manifest": m,
    "base": passes("base"),
    "adapter": passes("adapter"),
    "beats_base": passes("adapter")["passed"] > passes("base")["passed"],
    "envelope": env_p,
    "scores": scores_p,
    "created_utc": e.get("created_utc"),
}
json.dump(v, open(out_p, "w"), indent=1)
'''


def _sh(cmd: list, timeout: int = 60, env=None):
    """Run local shell command on THIS box (ASI2). <8 lines."""
    e = os.environ.copy()
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=e)
        return p.returncode, (p.stdout + p.stderr)[-500:]
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def install_helper() -> Path:
    """Write the verdict helper next to the watcher. <5 lines."""
    helper = Path(__file__).parent / "_verdict_helper.py"
    helper.write_text(VERDICT_PY)
    return helper


LOCK_STALE_S = 5 * 3600  # > 4h leg cap: a crashed watcher's lock self-heals


def _lock_stale(lock: Path) -> bool:
    """Lock older than LOCK_STALE_S (crash leftover). <5 lines."""
    try:
        return time.time() - lock.stat().st_mtime > LOCK_STALE_S
    except OSError:
        return False


def eval_step(step_dir: Path, helper: Path) -> dict:
    """Pull one adapter from bus, run leg1, write verdict back to bus. <20 lines."""
    lock = step_dir / ".eval_in_flight"
    if lock.exists() and not _lock_stale(lock):
        return {"run": step_dir.parent.name, "step": step_dir.name, "status": "SKIP_IN_FLIGHT"}
    lock.write_text(str(os.getpid()))
    try:
        return _eval_step_locked(step_dir, helper, lock)
    finally:
        lock.unlink(missing_ok=True)


def _eval_step_locked(step_dir: Path, helper: Path, lock: Path) -> dict:
    """Eval body, holding the in-flight lock. <18 lines."""
    man = json.loads((step_dir / get("ckpt_bus.manifest")).read_text())
    run, step = man["run"], man["step"]
    benchmark = man.get("benchmark_override") or str(EVAL_REPO / get("box.holdout_benchmark"))
    local_adapter = EVAL_ADAPTERS / run / step
    subprocess.run(["rm", "-rf", str(local_adapter)], check=False)
    (EVAL_ADAPTERS / run).mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["cp", "-r", str(step_dir / get("ckpt_bus.adapter_dir")), str(local_adapter)], check=True
    )
    _progress(run, step, "leg_running")  # live visibility during multi-hour legs
    out = Path("/tmp/eval_leg1") / run / step
    out.mkdir(parents=True, exist_ok=True)
    rc, tail = _sh(
        [
            "python3",
            str(EVAL_REPO / "scripts/run_holdout_leg1.py"),
            "--base-model",
            get("box.base_model"),
            "--adapter",
            str(local_adapter),
            "--step",
            step,
            "--out-dir",
            str(out),
            "--benchmark",
            benchmark,
        ],
        timeout=14400,  # 4h cap: 3 slices + probe
        env={"PYTHONUNBUFFERED": "1"},
    )
    if rc != 0:
        verdict = {"status": "LEG_FAILED", "rc": rc, "tail": tail[-200:]}
    else:
        envf = out / f"holdout_leg1_{step}.json"
        e = json.loads(envf.read_text())
        scoresf = EVAL_REPO / e["scores"]
        vout = step_dir / "verdict.json"
        rc2, tail2 = _sh(
            ["python3", str(helper), str(envf), str(scoresf), str(vout), str(step_dir / "manifest.json")],
            timeout=120,
        )
        if rc2:
            verdict = {"status": "VERDICT_HELPER_FAILED", "rc": rc2, "tail": tail2[-200:]}
            vout.write_text(json.dumps(verdict, indent=1))
        else:
            verdict = json.loads(vout.read_text())
    vpath = step_dir / "verdict.json"
    if verdict.get("status") not in ("OK", "VOID"):
        vpath.write_text(json.dumps(verdict, indent=1))
    return {"run": run, "step": step, "status": verdict.get("status"), "verdict_path": str(vpath)}


def scan_once(helper: Path) -> dict:
    """One bus scan: eval every manifest without a verdict. <12 lines."""
    results = []
    pending = [m.parent for m in sorted(BUS.glob("*/*/manifest.json")) if not (m.parent / "verdict.json").exists()]
    write_state(results, pending=len(pending))
    for m in sorted(BUS.glob("*/*/manifest.json")):
        step_dir = m.parent
        if (step_dir / "verdict.json").exists():
            continue
        try:
            results.append(eval_step(step_dir, helper))
        except Exception as exc:  # one bad step must never kill the loop
            results.append({"run": step_dir.parent.name, "step": step_dir.name, "status": "STEP_ERROR", "error": str(exc)[:200]})
            (step_dir / "verdict.json").write_text(json.dumps({"status": "STEP_ERROR", "error": str(exc)[:500]}, indent=1))
        write_state(results)
    return {"scanned": len(results), "results": results}


def _progress(run: str, step: str, phase: str) -> None:
    """Live in-progress marker inside state (hours-long legs stay visible). <8 lines."""
    try:
        d = json.loads(STATE.read_text()) if STATE.exists() else {}
    except json.JSONDecodeError:
        d = {}
    d["in_flight"] = {"run": run, "step": step, "phase": phase, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    STATE.write_text(json.dumps(d, indent=2) + "\n")


def write_state(results: list, pending: int = 0) -> None:
    """State on NAS for the Mac side. <6 lines."""
    STATE.write_text(
        json.dumps(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "host": os.uname().nodename,
                "last_scan_evaled": len(results),
                "pending": pending,
                "results": results[-10:],
            },
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    """Dispatch. <10 lines."""
    ap = argparse.ArgumentParser(description="Eval watcher (ASI2 side of ckpt bus)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    helper = install_helper()
    if args.status:
        print(STATE.read_text() if STATE.exists() else "NO_STATE_YET")
        return
    if args.loop:
        write_state([])  # immediate heartbeat: state exists from second zero
        while True:
            scan_once(helper)
            time.sleep(POLL_S)
    print(json.dumps(scan_once(helper), indent=2))


if __name__ == "__main__":
    main()

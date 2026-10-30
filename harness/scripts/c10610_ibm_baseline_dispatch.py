#!/usr/bin/env python3
"""C-10610 - dispatch the IBM Qiskit HumanEval BASELINE battery on ASI2
after the C-10608 v25 eval legs release the NPU.

Battery (4 sequential runs, fail-closed, one model load reused where
possible is NOT assumed — each run is an independent process):

  1. base  x qhe_completion    (139 tasks)
  2. base  x hard_instruction  (139 tasks)
  3. champion adapter (v22-resume step-1941, sha 373b6e6d...) x qhe_completion
  4. champion adapter x hard_instruction

Gate: waits for the C-10608 watcher to write DISPATCHED status (leg2
running) AND then for leg2's box processes to exit before starting — the
IBM battery must never contend with internal legs for the NPU pool.

Output: outputs/ibm_baseline_c10610/ on the box; envelope pulled local.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO / "harness"), str(REPO / "harness" / "scripts"), str(REPO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run_and_report as RR  # noqa: E402

BOX = "ASI2"
BOX_ROOT = "/root/work/quantum-gpt"
BOX_BASE_MODEL = "/root/work/filestorage/Qwen3.8-27B"
CHAMPION_ADAPTER = (
    BOX_ROOT + "/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter"
)
CHAMPION_SHA = "373b6e6dea3fa9e7b2a87fecb2b2fc455f4cdcc8d75ea59d554057b4992c2b3c"
C10608_STATUS_LOCAL = REPO / "outputs" / "C10608_v25_watch_status.json"
OUT_BOX = BOX_ROOT + "/outputs/ibm_baseline_c10610"
MAX_WAIT_SEC = 20 * 3600
POLL_SEC = 300


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def emit(stage: str, **kw) -> None:
    print(
        json.dumps(dict(stage=stage, ts_utc=now_utc(), **kw), ensure_ascii=False),
        flush=True,
    )


def box_exec(cmd: str, timeout: int = 60) -> dict:
    return RR.run_box(BOX, cmd, timeout=timeout)


def wait_for_c10608_status() -> bool:
    """Gate A: the C-10608 watcher status file must be DISPATCHED (leg2
    chained after leg1's envelope), meaning training finished and both
    internal legs were dispatched. A BLOCKED status is terminal ONLY if
    the live watcher process is gone (a live watcher overwrites the file
    as it progresses; stale BLOCKED from an earlier phase is not)."""
    deadline = time.time() + MAX_WAIT_SEC
    while time.time() < deadline:
        if C10608_STATUS_LOCAL.is_file():
            try:
                st = json.loads(C10608_STATUS_LOCAL.read_text())
            except json.JSONDecodeError:
                st = None
            if st and st.get("status") == "DISPATCHED":
                return True
            if st and st.get("status") == "BLOCKED" and not _watcher_alive():
                emit("fail_closed_c10608_blocked", reason=st.get("reason"))
                return False
        emit("waiting_for_c10608_dispatched")
        time.sleep(POLL_SEC)
    return False


def _watcher_alive() -> bool:
    import subprocess as sp

    r = sp.run(
        ["pgrep", "-f", "c10608_watch_v25_and_dispatch_legs"],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0


def wait_for_c10608_legs_clear() -> bool:
    """Gate B: no internal-leg processes AND no v25 trainer may hold NPUs."""
    deadline = time.time() + MAX_WAIT_SEC
    while time.time() < deadline:
        res = box_exec(
            "pgrep -fc 'run_holdout_leg|run_asi2_base_adapter_rubric_eval"
            "|qwen_sft_peft' || echo LEGS_CLEAR",
            timeout=60,
        )
        if res.get("status") == "PASS" and "LEGS_CLEAR" in str(res.get("stdout", "")):
            return True
        emit("npus_busy", detail=str(res.get("stdout", ""))[:80])
        time.sleep(POLL_SEC)
    return False


def verify_champion_adapter(max_tries: int = 6, backoff_s: int = 45) -> bool:
    """Retry loop: transport flaps must never read as a sha mismatch.
    Only a PASSING round-trip whose stdout lacks the pinned sha counts
    as a real mismatch (fail-closed)."""
    for attempt in range(1, max_tries + 1):
        res = box_exec(
            "sha256sum " + CHAMPION_ADAPTER + "/adapter_model.safetensors",
            timeout=120,
        )
        if res.get("status") == "PASS":
            return CHAMPION_SHA in str(res.get("stdout", ""))
        emit("champion_verify_transport_flap", attempt=attempt, detail=str(res.get("error"))[:150])
        time.sleep(backoff_s)
    return False


def launch_battery() -> dict:
    """One detached box-side bash chain running all 4 runs sequentially.

    Idempotent: each run is skipped if its envelope already exists; a run with
    a partial journal resumes from it (C-10610 container-restart recovery)."""
    inner = f"""
set -e
cd {BOX_ROOT}
mkdir -p {OUT_BOX}
echo "[battery] start $(date -u +%Y-%m-%dT%H:%M:%SZ)" > {OUT_BOX}/battery.log

if [ ! -f {OUT_BOX}/base_qhe/ibm_eval_qhe_completion_base.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \\
    --base-model {BOX_BASE_MODEL} \\
    --style qhe_completion \\
    --out-dir {OUT_BOX}/base_qhe \\
    $( [ -f {OUT_BOX}/base_qhe/journal.jsonl ] && echo --resume-journal {OUT_BOX}/base_qhe/journal.jsonl ) \\
    >> {OUT_BOX}/battery.log 2>&1
fi
echo "[battery] run1 base_qhe done $(date -u +%H:%M:%SZ)" >> {OUT_BOX}/battery.log

if [ ! -f {OUT_BOX}/base_hard/ibm_eval_hard_instruction_base.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \\
    --base-model {BOX_BASE_MODEL} \\
    --style hard_instruction \\
    --out-dir {OUT_BOX}/base_hard \\
    $( [ -f {OUT_BOX}/base_hard/journal.jsonl ] && echo --resume-journal {OUT_BOX}/base_hard/journal.jsonl ) \\
    >> {OUT_BOX}/battery.log 2>&1
fi
echo "[battery] run2 base_hard done $(date -u +%H:%M:%SZ)" >> {OUT_BOX}/battery.log

if [ ! -f {OUT_BOX}/champ_qhe/ibm_eval_qhe_completion_adapter.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \\
    --base-model {BOX_BASE_MODEL} \\
    --adapter {CHAMPION_ADAPTER} \\
    --style qhe_completion \\
    --out-dir {OUT_BOX}/champ_qhe \\
    $( [ -f {OUT_BOX}/champ_qhe/journal.jsonl ] && echo --resume-journal {OUT_BOX}/champ_qhe/journal.jsonl ) \\
    >> {OUT_BOX}/battery.log 2>&1
fi
echo "[battery] run3 champ_qhe done $(date -u +%H:%M:%SZ)" >> {OUT_BOX}/battery.log

if [ ! -f {OUT_BOX}/champ_hard/ibm_eval_hard_instruction_adapter.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \\
    --base-model {BOX_BASE_MODEL} \\
    --adapter {CHAMPION_ADAPTER} \\
    --style hard_instruction \\
    --out-dir {OUT_BOX}/champ_hard \\
    $( [ -f {OUT_BOX}/champ_hard/journal.jsonl ] && echo --resume-journal {OUT_BOX}/champ_hard/journal.jsonl ) \\
    >> {OUT_BOX}/battery.log 2>&1
fi
echo "[battery] run4 champ_hard done $(date -u +%H:%M:%SZ)" >> {OUT_BOX}/battery.log
echo BATTERY_DONE > {OUT_BOX}/DONE
"""
    # write the inner script via a heredoc-safe single file push
    script_path = REPO / "outputs" / "c10610_battery_inner.sh"
    script_path.parent.mkdir(exist_ok=True)
    script_path.write_text(inner)
    import subprocess as sp

    r = sp.run(
        [
            sys.executable,
            str(REPO / "harness" / "scripts" / "push_to_box.py"),
            BOX,
            str(script_path),
            BOX_ROOT + "/outputs/c10610_battery_inner.sh",
        ],
        capture_output=True,
        text=True,
    )
    if "VERIFY:" not in (r.stdout or "") + (r.stderr or ""):
        return dict(ok=False, detail=(r.stdout or "") + (r.stderr or ""))
    res = box_exec(
        # mkdir BEFORE the nohup redirect: OUT_BOX may not exist yet, and the
        # redirect would fail with ENOENT killing the battery instantly
        # (root cause of the 2026-10-30T01:03Z 'uch file or directory' launch).
        "mkdir -p "
        + OUT_BOX
        + " && nohup bash "
        + BOX_ROOT
        + "/outputs/c10610_battery_inner.sh > "
        + OUT_BOX
        + "/nohup.log 2>&1 & echo BATTERY_PID=$!",
        timeout=60,
    )
    pid = (str(res.get("stdout", "")).strip().splitlines() or [""])[-1]
    return dict(ok=True, pid=pid)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--skip-wait",
        action="store_true",
        help="skip waiting for C-10608 legs (NPU already free)",
    )
    args = ap.parse_args()

    emit("c10610_start")

    if not verify_champion_adapter():
        emit("fail_closed_champion_sha_mismatch")
        return 2
    emit("champion_verified", sha=CHAMPION_SHA[:16])

    if not args.skip_wait:
        # Gate A: C-10608 watcher must report DISPATCHED (leg2 chained) or
        # already-completed legs; Gate B: no leg/trainer/eval processes may
        # hold the NPU pool. Both gates avoid contending the IBM battery
        # with the v25 trainer or the internal eval legs.
        if not wait_for_c10608_status():
            emit("fail_closed_timeout_waiting_for_c10608")
            return 2
        emit("c10608_status_ok")
        if not wait_for_c10608_legs_clear():
            emit("fail_closed_timeout_waiting_for_legs")
            return 2
        emit("legs_clear")
    else:
        emit("skip_wait")

    d = launch_battery()
    if not d.get("ok"):
        emit("fail_closed_battery_launch", detail=str(d.get("detail"))[:300])
        return 2
    emit("battery_dispatched", pid=d.get("pid"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

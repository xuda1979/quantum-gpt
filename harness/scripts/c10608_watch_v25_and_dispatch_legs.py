#!/usr/bin/env python3
"""C-10608 - watch the v25 SFT run (sft-27b-q38-v25-new50-*) on ASI2 until the
final adapter is saved ("save_done" log stage + <run>/adapter/ present), then
auto-dispatch the C-10608 promotion legs on the FROZEN v2 holdout
(sapo_promotion_holdout_v2_18.txt, 18 leak-audited tasks):

  leg1: parallel-3-slice via scripts/run_holdout_leg1.py (seeded)
  leg2: independent sequential single-slice via scripts/run_holdout_leg2.py

Both legs use --benchmark sapo_promotion_holdout_v2_18.txt (sha
236c423d8b7a89fa98922ee3dc88d34baf4c551dbbec38119aed00eeb9942bc6,
identical local/box). The v25 training corpus (C-10606, 50 tasks,
outputs/C10606_v25_train_chatml.jsonl) is verified disjoint from the 18
holdout ids (checked local AND box side: overlap 0).

Fail-closed: on any anomaly (trainer dead without save_done, loss_alarm
storm, lock contention timeout) the watcher records a BLOCKED status file
and exits non-zero WITHOUT dispatching.

Usage:
  nohup python3 harness/scripts/c10608_watch_v25_and_dispatch_legs.py \
      --run sft-27b-q38-v25-new50-20261029T052951Z \
      > logs/c10608_watch.log 2>&1 &

"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO / "harness"), str(REPO / "harness" / "scripts"), str(REPO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import harness_lib as H  # noqa: E402
import run_and_report as RR  # noqa: E402

BOX = "ASI2"
BOX_ROOT = "/root/work/quantum-gpt"
BOX_BASE_MODEL = "/root/work/filestorage/Qwen3.8-27B"
BOX_BENCH_V2 = f"{BOX_ROOT}/evals/benchmarks/sapo_promotion_holdout_v2_18.txt"
BENCH_V2_SHA256 = "236c423d8b7a89fa98922ee3dc88d34baf4c551dbbec38119aed00eeb9942bc6"
ASI2_EVAL_LOCK = REPO / "harness" / "state" / "locks" / "asi2-eval.lock"
MAX_TRAIN_WAIT_SEC = 6 * 3600  # v25 ETA ~5.3h; give it 6h hard cap
POLL_SEC = 300

LEG1_SEED = "c10608-v25-final-v2-leg1"
LEG2_SEED = "c10608-v25-final-v2-leg2"


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def emit(stage: str, **kw) -> None:
    rec = dict(stage=stage, ts_utc=now_utc(), **kw)
    print(json.dumps(rec, ensure_ascii=False), flush=True)


def box_exec(cmd: str, timeout: int = 60) -> dict:
    return RR.run_box(BOX, cmd, timeout=timeout)


def sha256_local(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wait_for_training_done(run: str) -> dict:
    """Poll box until trainer saves final adapter. Fail-closed on death."""
    log_path = f"{BOX_ROOT}/logs/{run}.log"
    adapter_dir = f"{BOX_ROOT}/outputs/{run}/adapter"
    deadline = time.time() + MAX_TRAIN_WAIT_SEC
    last_step = -1
    while time.time() < deadline:
        res = box_exec(
            "grep -o '\"step\": [0-9]*' " + log_path + " | tail -1; "
            'grep -c \'"stage": "save_done"\' ' + log_path + "; "
            "test -f " + adapter_dir + "/adapter_model.safetensors && echo ADAPTER_OK; "
            "pgrep -fc qwen_sft_peft || echo TRAINER_DEAD",
            timeout=90,
        )
        if res.get("status") != "PASS":
            emit("poll_transport_flap", detail=str(res.get("error"))[:200])
            time.sleep(30)
            continue
        out = str(res.get("stdout", ""))
        lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
        try:
            last_step = int(lines[0].split()[-1]) if lines else last_step
            save_done = int(lines[1]) if len(lines) > 1 else 0
        except (ValueError, IndexError):
            save_done = 0
        adapter_ok = any("ADAPTER_OK" in ln for ln in lines)
        trainer_dead = any("TRAINER_DEAD" in ln for ln in lines)

        if save_done > 0 and adapter_ok:
            emit("training_done", run=run, last_step=last_step)
            return dict(ok=True, last_step=last_step)
        if trainer_dead and save_done == 0:
            emit("fail_closed_trainer_dead_without_save", run=run, last_step=last_step)
            return dict(ok=False, reason="trainer_dead_without_save", last_step=last_step)
        emit("poll", run=run, last_step=last_step, save_done=save_done, adapter_ok=adapter_ok)
        time.sleep(POLL_SEC)
    emit("fail_closed_timeout", run=run, last_step=last_step)
    return dict(ok=False, reason="timeout", last_step=last_step)


def verify_final_adapter(run: str) -> dict:
    """Box-side sha256 of the final adapter; recorded for the dispatch record."""
    adapter_dir = f"{BOX_ROOT}/outputs/{run}/adapter"
    res = box_exec(
        "sha256sum " + adapter_dir + "/adapter_model.safetensors && "
        "stat -c %s " + adapter_dir + "/adapter_model.safetensors",
        timeout=120,
    )
    out = str(res.get("stdout", "")).strip()
    if res.get("status") != "PASS" or not out:
        return dict(ok=False, detail=out[:300])
    parts = out.split()
    return dict(ok=True, adapter_sha256=parts[0], adapter_bytes=parts[-1])


def verify_bench_box() -> bool:
    res = box_exec("sha256sum " + BOX_BENCH_V2, timeout=60)
    return BENCH_V2_SHA256 in str(res.get("stdout", ""))


def dispatch_leg1(run: str, out_dir_box: str) -> dict:
    """Launch leg1 (parallel-3-slice) on the box, nohup detached."""
    adapter = f"{BOX_ROOT}/outputs/{run}/adapter"
    cmd = (
        "cd " + BOX_ROOT + " && mkdir -p " + out_dir_box + " && "
        "nohup python3 " + BOX_ROOT + "/scripts/run_holdout_leg1.py "
        "--base-model " + BOX_BASE_MODEL + " "
        "--adapter " + adapter + " "
        "--step step-final-v25 "
        "--out-dir " + out_dir_box + " "
        "--box " + BOX + " "
        "--benchmark " + BOX_BENCH_V2 + " "
        "--seed " + LEG1_SEED + " "
        "> " + out_dir_box + "/dispatch.log 2>&1 & echo LEG1_PID=$!"
    )
    res = box_exec(cmd, timeout=120)
    pid_line = (str(res.get("stdout", "")).strip().splitlines() or [""])[-1]
    return dict(status=res.get("status"), pid=pid_line)


def dispatch_leg2(run: str, out_dir_box: str) -> dict:
    """Launch leg2 (sequential single-slice) on the box, nohup detached.

    leg2 is fired only AFTER leg1's envelope lands (two-leg chain), so the
    two legs never contend for the NPU concurrently.
    """
    adapter = f"{BOX_ROOT}/outputs/{run}/adapter"
    cmd = (
        "cd " + BOX_ROOT + " && mkdir -p " + out_dir_box + " && "
        "nohup python3 " + BOX_ROOT + "/scripts/run_holdout_leg2.py "
        "--base-model " + BOX_BASE_MODEL + " "
        "--adapter " + adapter + " "
        "--step step-final-v25 "
        "--out-dir " + out_dir_box + " "
        "--box " + BOX + " "
        "--benchmark " + BOX_BENCH_V2 + " "
        "--seed " + LEG2_SEED + " "
        "> " + out_dir_box + "/dispatch.log 2>&1 & echo LEG2_PID=$!"
    )
    res = box_exec(cmd, timeout=120)
    pid_line = (str(res.get("stdout", "")).strip().splitlines() or [""])[-1]
    return dict(status=res.get("status"), pid=pid_line)


def wait_for_leg1_envelope(out_dir_box: str, max_sec: int = 5 * 3600) -> bool:
    """Wait until leg1 envelope holdout_leg1_*.json appears on the box."""
    deadline = time.time() + max_sec
    while time.time() < deadline:
        res = box_exec(
            "ls " + out_dir_box + "/holdout_leg1_*.json 2>/dev/null | head -3",
            timeout=60,
        )
        if res.get("status") == "PASS" and ".json" in str(res.get("stdout", "")):
            return True
        emit("leg1_waiting", out_dir=out_dir_box)
        time.sleep(300)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="C-10608 v25 watcher + leg dispatch")
    ap.add_argument(
        "--run", required=True, help="v25 run id, e.g. sft-27b-q38-v25-new50-20261029T052951Z"
    )
    ap.add_argument(
        "--skip-wait", action="store_true", help="skip training wait (final adapter already saved)"
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    emit("watcher_start", run=args.run, box=BOX)

    # 0) bench integrity, both sides
    if not verify_bench_box():
        emit("fail_closed_bench_sha_mismatch", bench=BOX_BENCH_V2)
        return 1
    emit("bench_verified", bench=BOX_BENCH_V2, sha256=BENCH_V2_SHA256)

    # 1) wait for training
    if args.skip_wait:
        emit("skip_wait_requested")
        tstate = dict(ok=True, last_step=None)
    else:
        tstate = wait_for_training_done(args.run)
        if not tstate.get("ok"):
            _write_status("BLOCKED", tstate.get("reason"), args.run)
            return 2

    # 2) verify final adapter
    av = verify_final_adapter(args.run)
    if not av.get("ok"):
        _write_status("BLOCKED", "final_adapter_verify_failed", args.run)
        return 2
    emit("final_adapter_verified", **av)

    if args.dry_run:
        emit("dry_run_stop_after_verify")
        return 0

    # 3) asi2-eval.lock (protects against concurrent eval legs)
    tok = H.acquire_lock(str(ASI2_EVAL_LOCK))
    if tok is None:
        emit("fail_closed_lock_held")
        _write_status("BLOCKED", "asi2-eval.lock held by live holder", args.run)
        return 2
    emit("lock_acquired")

    try:
        # 4) dispatch leg1
        leg1_out = f"{BOX_ROOT}/outputs/eval_leg1_c10608_v25_final"
        d1 = dispatch_leg1(args.run, leg1_out)
        emit("leg1_dispatched", **d1)
        if d1.get("status") != "PASS":
            _write_status("BLOCKED", "leg1_dispatch_failed", args.run)
            return 2

        # 5) wait for leg1 envelope, then dispatch leg2
        if not wait_for_leg1_envelope(leg1_out):
            emit("fail_closed_leg1_envelope_timeout")
            _write_status("BLOCKED", "leg1_envelope_timeout", args.run)
            return 2
        emit("leg1_envelope_seen")

        leg2_out = f"{BOX_ROOT}/outputs/eval_leg2_c10608_v25_final"
        d2 = dispatch_leg2(args.run, leg2_out)
        emit("leg2_dispatched", **d2)
        _write_status("DISPATCHED", "leg2_running", args.run)
        return 0
    finally:
        try:
            H.release_lock(str(ASI2_EVAL_LOCK), tok)
            emit("lock_released")
        except Exception:
            pass


def _write_status(status: str, reason: str, run: str) -> None:
    out = REPO / "outputs" / "C10608_v25_watch_status.json"
    out.write_text(
        json.dumps(
            dict(
                status=status,
                reason=reason,
                run=run,
                ts_utc=now_utc(),
                no_fabrication=True,
            ),
            indent=1,
        )
        + "\n"
    )
    emit("status_written", status=status, reason=reason)


if __name__ == "__main__":
    raise SystemExit(main())

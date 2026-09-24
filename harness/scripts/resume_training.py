#!/usr/bin/env python3
"""resume_training.py — resume the canonical training thread from its latest checkpoint.

The canonical thread today: SFT on Qwen3.8-27B (GOAL model) over verified-chat
data — runs matching outputs/sft-27b-q38-v10*. Finds the run's LATEST
checkpoints/step-N/adapter and relaunches torchrun with --adapter-init.

Gate chain before any launch (fail-closed, one skip = no launch):
  1. compile gate: on-box training tree py_compiles
  2. no trainer already running (double-launch guard)

Usage:
    python3 harness/scripts/resume_training.py --dry-run
    python3 harness/scripts/resume_training.py            # gate + launch + boot-verify
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from harness_config import get  # noqa: E402
from run_and_report import run_box  # noqa: E402

BOX = "ASI3"
STATE = REPO / "harness" / "state" / "resume_training.json"

# --adapter-init needs the adapter/ subdir (contains adapter_config.json),
# not the step-N dir itself.
FIND_LATEST_SH = (
    "latest=$(ls -d {repo}/outputs/sft-27b-q38-v10*/checkpoints/step-*/adapter 2>/dev/null "
    "| sed -E 's#.*/step-([0-9]+)/adapter#\\1 &#' "
    "| sort -n -k1 | tail -1 | cut -d' ' -f2-); "
    "echo LATEST=$latest"
)


def parse_latest_checkpoint(paths) -> str | None:
    """Return the path with the numerically-max step-N, or None if empty.
    <8 lines. Correct numeric ordering (step-25 > step-9 > step-7), immune
    to the leading run-name digits (sft-27b-*)."""
    best = None
    best_n = -1
    for p in paths or []:
        m = re.search(r"step-(\d+)/adapter$", p)
        if not m:
            continue
        n = int(m.group(1))
        if n > best_n:
            best_n, best = n, p
    return best
def latest_run_advancing(lines, now_iso=None, freshness_window_s=600):
    import json as _json
    from datetime import datetime, timezone
    def _ts(rec):
        raw = rec.get('timestamp_utc') if rec else None
        if not raw:
            return None
        try:
            return datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
        except ValueError:
            return None
    text = chr(10).join((lines or []))
    dec = _json.JSONDecoder()
    recs = []
    i = 0
    n = len(text)
    while i < n:
        j = text.find(chr(123), i)
        if j == -1:
            break
        try:
            obj, k = dec.raw_decode(text, j)
        except _json.JSONDecodeError:
            i = j + 1
            continue
        if isinstance(obj, dict):
            recs.append(obj)
        i = k
    if not recs:
        return dict(advancing=False, latest_step=None)
    last = recs[-1]
    latest_step = last.get('step')
    advancing = False
    if len(recs) >= 2:
        prev_step = recs[-2].get('step')
        if isinstance(latest_step, int) and isinstance(prev_step, int):
            advancing = latest_step > prev_step
    if now_iso:
        now = datetime.fromisoformat(str(now_iso).replace('Z', '+00:00'))
        last_ts = _ts(last)
        if last_ts and (now - last_ts).total_seconds() > freshness_window_s:
            advancing = False
    elif len(recs) < 2:
        advancing = False
    return dict(advancing=advancing, latest_step=latest_step)

PGUARD_SH = "pgrep -f 'qwen_sft_peft|torchrun.*qwen_sft' >/dev/null && echo TRAINER_RUNNING || echo TRAINER_DOWN"
COMPILE_SH = (
    "bad=0; for f in /root/work/training/*.py; do "
    'python3 -m py_compile "$f" 2>/dev/null || bad=1; done; echo GATE_RC=$bad'
)


# C-9692: compact output immune to run_box stdout truncation. Sort by version
# on the box so only the numerically-max step-N adapter path is echoed (a
# whole-tree ls -d could drop step-166 when run_box truncates to last 2000
# chars, returning a stale step-97). sort -V orders step-9 < step-25 < step-166.
LS_ALL_SH = (
    # C-9746: rank candidates by adapter mtime (newest first), then max step
    # within the newest run. A warm-consumed shard checkpoint (older mtime)
    # must never win over the fresher run that consumed it.
    "for p in {repo}/outputs/sft-27b-q38-v10*/checkpoints/step-*/adapter; do "
    "[ -e \"$p/adapter_config.json\" ] || continue; "
    "stat -c '%Y %n' \"$p\" 2>/dev/null; done "
    "| sort -n | tail -40"
)


def find_latest_checkpoint(box: str = BOX):
    """C-9746: the LATEST-RUN's newest checkpoint, by mtime rank.

    The box emits '<mtime> <path>' lines sorted newest-first (LS_ALL_SH).
    Rank = (mtime desc, step desc). Rationale: resume must continue the run
    that most recently banked a checkpoint. A warm-consumed shard checkpoint
    (e.g. step-166 used to init a resume run) has an OLDER mtime than the
    resume run's own checkpoints; picking the global max step instead
    discarded the newer run's progress (C-9746 incident, 2026-09-24)."""
    r = run_box(box, LS_ALL_SH.format(repo=get("box.repo_nas")), timeout=30)
    best = None
    best_key = None
    for ln in r.get("stdout", "").splitlines():
        parts = ln.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        mtime, path = int(parts[0]), parts[1].strip()
        m = re.search(r"step-(\d+)/adapter$", path)
        if not m:
            continue
        key = (mtime, int(m.group(1)))
        if best_key is None or key > best_key:
            best_key, best = key, path
    return best


def trainer_running(box: str = BOX):
    """Double-launch guard. Returns (running, box_up). <6 lines."""
    r = run_box(box, PGUARD_SH, timeout=20)
    up = r.get("status") != "BOX_DOWN"
    return ("TRAINER_RUNNING" in r.get("stdout", "")) if up else False, up


def compile_gate(box: str = BOX):
    """On-box tree compiles. Returns (ok, box_up). <6 lines."""
    r = run_box(box, COMPILE_SH, timeout=120)
    up = r.get("status") != "BOX_DOWN"
    return ("GATE_RC=0" in r.get("stdout", "")) if up else False, up


def launch_cmd(
    checkpoint: str,
    run_name: str,
    checkpoint_interval_seconds: int = 300,
    exclude_devices: list | None = None,
) -> str:
    """The setsid resume command (current CLI, not the stale template). <14 lines.

    2026-09-23 C-9631: clear leaked NPU device state BEFORE launching the
    authoritative SFT resume to break the recurring 507015 (ACL stream sync
    fail) treadmill. Each 507015 crash leaks device semaphores/HBM; relaunch
    reuses polluted devices and crashes again at the same step. Kill BOTH the
    residual SFT and the retired GRPO families (the 14:52Z SFT OOM was
    retired-GRPO holding all 8 NPUs), wait for NPU release, then launch.
    Order is covered by test_resume_npu_reset_before_launch.

    exclude_devices: a faulty NPU die (measured: chip 5 fires aicore 507015)
    is excluded by setting ASCEND_RT_VISIBLE_DEVICES to the healthy subset and
    dropping --nproc_per_node to match. Covered by test_c9631_exclude_faulty_npu."""
    total = [0, 1, 2, 3, 4, 5, 6, 7]
    visible = [d for d in total if d not in (exclude_devices or [])]
    nproc = len(visible)
    vis_str = ",".join(str(d) for d in visible)
    return (
        f"cd {get('box.repo_nas')} && mkdir -p outputs/{run_name} logs && "
        f"pkill -f 'grpo_trainer' 2>/dev/null; "
        f"npu-smi info >/dev/null 2>&1; "
        f"pkill -f 'qwen_sft_peft' 2>/dev/null; sleep 20; "
        f"ASCEND_RT_VISIBLE_DEVICES={vis_str} ASCEND_LAUNCH_BLOCKING=1 "
        f"setsid nohup torchrun --nproc_per_node={nproc} training/qwen_sft_peft.py "
        f"--model-name {get('box.base_model')} "
        f"--train-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/train_chatml.jsonl "
        f"--adapter-init {checkpoint} "
        f"--output-dir outputs/{run_name} "
        "--max-length 1024 --num-epochs 6 --per-device-batch-size 1 "
        "--gradient-accumulation-steps 4 --max-steps 0 --log-steps 1 "
        "--learning-rate 2e-5 --lora-rank 16 --lora-alpha 32 --lora-dropout 0.0 "
        "--target-modules q_proj v_proj o_proj gate_proj up_proj down_proj "
        "--train-on-completions-only --gradient-checkpointing "
        f"--max-trainable-parameters 500000000 --checkpoint-interval-seconds {checkpoint_interval_seconds} "
        "--overwrite-output-dir "
        f"> logs/{run_name}.log 2>&1 & echo LAUNCHED pid=$!"
    )


def boot_verify(box: str, run_name: str) -> dict:
    """Alive + log advancing, 3 polls x 20s. <12 lines."""
    for _ in range(3):
        time.sleep(20)
        r = run_box(
            box,
            f"pgrep -f 'qwen_sft_peft.py' | head -1; "
            f"grep -c '\"stage\"' {get('box.repo_nas')}/logs/{run_name}.log 2>/dev/null",
            timeout=20,
        )
        out = r.get("stdout", "").strip().splitlines()
        pid = out[0] if out and out[0].isdigit() else ""
        stages = out[1] if len(out) > 1 else "0"
        if pid and int(stages or 0) > 0:
            return {"alive": True, "pid": pid, "log_stages": stages}
    return {"alive": False, "pid": pid if "pid" in dir() else "", "log_stages": stages}


def load_die_exclusions(box='ASI3'):
    """Read the persistent die-exclusion ledger for a box. C-9689.

    Exclusion knowledge (dies proven faulty by past 507015 aicore crashes) is
    persisted in harness/state/np_die_exclusions.json so no relaunch loses it.
    Returns the box's dies_excluded list, or [] when absent/unknown. <12 lines."""
    p = REPO / 'harness' / 'state' / 'np_die_exclusions.json'
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    if data.get('box') != box:
        return []
    dies = data.get('dies_excluded')
    if not isinstance(dies, list):
        return []
    out = []
    for d in dies:
        try:
            out.append(int(d))
        except (TypeError, ValueError):
            continue
    return out


def resume(
    dry_run: bool = False,
    checkpoint_interval_seconds: int = 300,
    exclude_devices: list | None = None,
) -> dict:
    """Gate chain + launch + boot-verify. <20 lines."""
    if exclude_devices is None:
        exclude_devices = load_die_exclusions(BOX)  # C-9689 auto-load
    run_name = f"sft-27b-q38-v10-resume-{time.strftime('%Y%m%dT%H%M%SZ')}"
    latest = find_latest_checkpoint()
    result = {"run_name": run_name, "latest_checkpoint": latest}
    if not latest:
        return {**result, "status": "NO_CHECKPOINT"}
    running, up = trainer_running()
    if not up:
        return {**result, "status": "BOX_DOWN"}
    if running:
        return {**result, "status": "SKIP_TRAINER_ALREADY_RUNNING"}
    cok, up = compile_gate()
    if not up:
        return {**result, "status": "BOX_DOWN"}
    if not cok:
        return {**result, "status": "BLOCKED_COMPILE_GATE"}
    cmd = launch_cmd(
        latest,
        run_name,
        checkpoint_interval_seconds=checkpoint_interval_seconds,
        exclude_devices=exclude_devices,
    )
    if dry_run:
        return {**result, "status": "DRY_RUN", "command": cmd}
    r = run_box(BOX, cmd, timeout=30)
    result["launch"] = r.get("status")
    result["boot"] = boot_verify(BOX, run_name)
    result["status"] = "RESUMED" if result["boot"]["alive"] else "BOOT_FAILED"
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    """Dispatch. <6 lines."""
    ap = argparse.ArgumentParser(description="Resume canonical training thread")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=300,
        help="C-9629/C-9631 507015 mitigation: 0 = save only at end (breaks step-10 crash)",
    )
    ap.add_argument(
        "--exclude-devices",
        type=str,
        default=None,
        help="faulty NPU die ids to exclude (e.g. 5 = chip-5 aicore 507015), comma-separated",
    )
    args = ap.parse_args()
    exclude = (
        [int(x) for x in args.exclude_devices.split(",") if x.strip()]
        if args.exclude_devices
        else None
    )
    print(
        json.dumps(
            resume(args.dry_run, args.checkpoint_interval_seconds, exclude), indent=2, default=str
        )
    )


if __name__ == "__main__":
    main()

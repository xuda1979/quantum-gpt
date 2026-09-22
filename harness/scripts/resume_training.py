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
    "| sort -t- -k2 -n | tail -1); "
    "echo LATEST=$latest"
)
PGUARD_SH = "pgrep -f 'torchrun|qwen_sft_peft|grpo_trainer' >/dev/null && echo TRAINER_RUNNING || echo TRAINER_DOWN"
COMPILE_SH = (
    "bad=0; for f in /root/work/training/*.py; do "
    "python3 -m py_compile \"$f\" 2>/dev/null || bad=1; done; echo GATE_RC=$bad"
)


def find_latest_checkpoint(box: str = BOX):
    """Latest step-N adapter of the canonical run. <8 lines."""
    r = run_box(box, FIND_LATEST_SH.format(repo=get("box.repo_nas")), timeout=30)
    for ln in r.get("stdout", "").splitlines():
        if ln.startswith("LATEST=/") and ln.strip() != "LATEST=":
            return ln.split("=", 1)[1].strip()
    return None


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


def launch_cmd(checkpoint: str, run_name: str) -> str:
    """The setsid resume command (current CLI, not the stale template). <12 lines."""
    return (
        f"cd {get('box.repo_nas')} && mkdir -p outputs/{run_name} logs && "
        f"setsid nohup torchrun --nproc_per_node=8 training/qwen_sft_peft.py "
        f"--model-name {get('box.base_model')} "
        f"--train-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/train_chatml.jsonl "
        f"--adapter-init {checkpoint} "
        f"--output-dir outputs/{run_name} "
        "--max-length 1024 --num-epochs 6 --per-device-batch-size 1 "
        "--gradient-accumulation-steps 4 --max-steps 0 --log-steps 1 "
        "--learning-rate 2e-5 --lora-rank 16 --lora-alpha 32 --lora-dropout 0.0 "
        "--target-modules q_proj v_proj o_proj gate_proj up_proj down_proj "
        "--train-on-completions-only --gradient-checkpointing "
        "--max-trainable-parameters 500000000 --checkpoint-interval-seconds 300 "
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


def resume(dry_run: bool = False) -> dict:
    """Gate chain + launch + boot-verify. <20 lines."""
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
    cmd = launch_cmd(latest, run_name)
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
    args = ap.parse_args()
    print(json.dumps(resume(args.dry_run), indent=2, default=str))


if __name__ == "__main__":
    main()

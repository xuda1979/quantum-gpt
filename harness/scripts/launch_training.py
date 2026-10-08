#!/usr/bin/env python3
"""launch_training.py — launch GRPO training with setsid (survives daemon restarts).

The old approach used `nohup` alone, which dies when the daemon's process group
is killed by `launchctl kickstart -k`. Using `setsid` creates a new session
that is fully detached from the daemon's process group.

Usage:
    python3 harness/scripts/launch_training.py --dry-run
    python3 harness/scripts/launch_training.py --box ASI3 --benchmark v9
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from run_and_report import run_box  # noqa: E402

PROBE_PATH = REPO / "harness" / "state" / "probes" / "train.json"

# The training command template — uses setsid + nohup for full detachment
TRAIN_CMD = (
    "setsid nohup torchrun --nproc_per_node=8 "
    "training/grpo_trainer.py "
    "--benchmark {benchmark} "
    "--output_dir /vllm-workspace/{run_name} "
    "--resume_from {resume_from} "
    "> /vllm-workspace/{run_name}/training.log 2>&1 &"
)


def _run_name() -> str:
    """Generate run name. <3 lines."""
    return f"sapo-27b-ai-{time.strftime('%Y%m%dT%H%M%SZ')}"


def _probe_data(run_name: str, benchmark: str) -> dict:
    """Build initial probe data. <10 lines."""
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "LAUNCHING",
        "run": run_name,
        "benchmark": benchmark,
        "trainer_pid": None,
        "last_checkpoint_step": 0,
        "last_checkpoint_loss": None,
        "resume_from": "scratch",
        "fail_closed_gate": {"v10_launch": "BLOCKED" if "v10" in benchmark else "OK"},
    }


def _write_probe(probe: dict) -> None:
    """Write probe to state. <5 lines."""
    PROBE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROBE_PATH.write_text(json.dumps(probe, indent=2))


def _launch_cmd(box: str, benchmark: str, resume_from: str) -> str:
    """Build the setsid launch command. <8 lines."""
    run_name = _run_name()
    cmd = TRAIN_CMD.format(benchmark=benchmark, run_name=run_name, resume_from=resume_from)
    return cmd


def compile_gate(box: str) -> dict:
    """Refuse to launch unless the on-box training tree compiles. Contract:
    no_training_without_compile_gate — today's two crashes were mid-push
    import races. py_compile sweep of /root/work/training/*.py. <12 lines."""
    sh = (
        "bad=0; for f in /root/work/training/*.py; do "
        "python3 -m py_compile \"$f\" 2>/dev/null || { echo \"BAD:$f\"; bad=1; }; done; "
        "echo GATE_RC=$bad"
    )
    r = run_box(box, sh, timeout=120)
    out = r.get("stdout", "")
    ok = "GATE_RC=0" in out
    bad_files = [ln[4:] for ln in out.splitlines() if ln.startswith("BAD:")]
    return {"ok": ok, "bad_files": bad_files, "status": r.get("status")}


def launch(box: str, benchmark: str, resume_from: str) -> dict:
    """Gate on compile, then launch training on box with setsid. <15 lines."""
    gate = compile_gate(box)
    if not gate["ok"]:
        probe = _probe_data(_run_name(), benchmark)
        probe["launch_result"] = "BLOCKED_COMPILE_GATE"
        probe["gate"] = gate
        _write_probe(probe)
        return {"blocked": True, "gate": gate, "probe": probe}
    run_name = _run_name()
    cmd = _launch_cmd(box, benchmark, resume_from)
    result = run_box(box, cmd, timeout=15)
    probe = _probe_data(run_name, benchmark)
    probe["launch_command"] = cmd
    probe["launch_result"] = result.get("status")
    probe["gate"] = gate
    _write_probe(probe)
    return {"run_name": run_name, "command": cmd, "result": result, "probe": probe}


def main():
    """Argparse dispatch. <15 lines."""
    ap = argparse.ArgumentParser(description="Launch training with setsid")
    ap.add_argument("--box", default="ASI3")
    ap.add_argument(
        "--benchmark", default="evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt"
    )
    ap.add_argument("--resume-from", default="scratch")
    ap.add_argument("--dry-run", action="store_true", help="print command, don't launch")
    args = ap.parse_args()

    if args.dry_run:
        cmd = _launch_cmd(args.box, args.benchmark, args.resume_from)
        run_name = _run_name()
        print(f"DRY RUN — would execute on {args.box}:")
        print(f"  command: {cmd}")
        print(f"  run_name: {run_name}")
        print(f"  probe: {PROBE_PATH}")
        print("  setsid: YES (survives daemon restart)")
    else:
        result = launch(args.box, args.benchmark, args.resume_from)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

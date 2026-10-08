#!/usr/bin/env python3
"""Training-aware eval tracker.

Monitors active training runs and automatically kicks off the comprehensive
eval harness once the final adapter is written. Designed to run persistently
on the NPU machine as a background daemon.

Usage (inside Huanxin NPU env):
  # Watch a training output dir and auto-eval when adapter appears:
  python3 evals/subsystem/tracker.py watch \\
      --output-dir /root/work/quantum-gpt/outputs/qg-35b-glm52-distill-sft-...-20260706T081105Z \\
      --base-model /tmp/qwen35b_decompressed_for_training_asi3 \\
      --eval-output-dir /root/work/quantum-gpt/outputs/ \\
      --device npu \\
      --npu-max-memory-gib 50

  # List status of all recent training output dirs:
  python3 evals/subsystem/tracker.py status \\
      --outputs-root /root/work/quantum-gpt/outputs

  # Print the post-training eval command for a given training output dir:
  python3 evals/subsystem/tracker.py print-eval-cmd \\
      --output-dir /root/work/quantum-gpt/outputs/qg-35b-glm52-distill-sft-... \\
      --base-model /tmp/qwen35b_decompressed_for_training_asi3
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HARNESS = ROOT / "evals" / "subsystem" / "harness.py"
REPORTER = ROOT / "evals" / "subsystem" / "reporter.py"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(msg: str, **kw: Any) -> None:
    print(json.dumps({"ts": _now_utc(), **kw, "msg": msg}), flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Training output dir helpers
# ─────────────────────────────────────────────────────────────────────────────

def adapter_ready(output_dir: Path) -> bool:
    """Return True if the final adapter (not just a checkpoint) is written."""
    adapter_dir = output_dir / "adapter"
    return (adapter_dir / "adapter_config.json").exists()


def find_latest_checkpoint(output_dir: Path) -> Path | None:
    """Return the highest-step checkpoint in an output dir, or None."""
    ckpt_dirs = sorted(
        (output_dir / "checkpoints").glob("step-*/adapter"),
        key=lambda p: int(p.parent.name.replace("step-", "")),
    )
    return ckpt_dirs[-1] if ckpt_dirs else None


def read_run_config(output_dir: Path) -> dict[str, Any]:
    for name in ("run_config.json", "config.json"):
        path = output_dir / name
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                pass
    return {}


def scan_outputs(outputs_root: Path, max_age_days: int = 7) -> list[dict[str, Any]]:
    """Scan an outputs root dir and return status for recent training runs."""
    cutoff = time.time() - max_age_days * 86400
    rows = []
    for d in sorted(outputs_root.iterdir()):
        if not d.is_dir():
            continue
        try:
            mtime = d.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            continue
        ckpt_dirs = sorted(
            (d / "checkpoints").glob("step-*/adapter"),
            key=lambda p: int(p.parent.name.replace("step-", "")),
        ) if (d / "checkpoints").exists() else []
        rows.append({
            "dir": str(d),
            "name": d.name,
            "adapter_ready": adapter_ready(d),
            "n_checkpoints": len(ckpt_dirs),
            "latest_checkpoint_step": (
                int(ckpt_dirs[-1].parent.name.replace("step-", "")) if ckpt_dirs else None
            ),
            "run_config": read_run_config(d),
            "mtime_utc": datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# watch: poll until adapter is ready, then eval
# ─────────────────────────────────────────────────────────────────────────────

def cmd_watch(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    _log("watch_start", output_dir=str(output_dir), poll_secs=args.poll_secs)

    # Wait for adapter
    while not adapter_ready(output_dir):
        ckpt = find_latest_checkpoint(output_dir)
        ckpt_info = str(ckpt) if ckpt else "none"
        _log("waiting_for_adapter", latest_checkpoint=ckpt_info)
        time.sleep(args.poll_secs)

    _log("adapter_ready", output_dir=str(output_dir))

    # Build eval command
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    eval_name = f"eval-{output_dir.name[:40]}-{ts}"
    eval_output = Path(args.eval_output_dir) / f"{eval_name}.json"
    log_path    = Path(args.eval_output_dir).parent / "logs" / f"{eval_name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(HARNESS),
        "--base-model",  args.base_model,
        "--adapter",     str(output_dir / "adapter"),
        "--output",      str(eval_output),
        "--device",      args.device,
        "--npu-max-memory-gib", str(args.npu_max_memory_gib),
        "--max-new-tokens", str(args.max_new_tokens),
        "--k", str(args.k),
        "--tasks", args.tasks,
    ]
    if args.eval_file:
        cmd += ["--eval-file", args.eval_file]

    _log("eval_launch", cmd=" ".join(cmd), log=str(log_path))

    with open(log_path, "w") as log_fh:
        proc = subprocess.run(cmd, stdout=log_fh, stderr=log_fh)

    _log("eval_complete", returncode=proc.returncode, output=str(eval_output))

    # Auto-generate Markdown report
    if proc.returncode == 0 and eval_output.exists():
        report_path = eval_output.with_suffix(".md")
        rep_cmd = [
            sys.executable, str(REPORTER), "single",
            "--eval", str(eval_output),
            "--label", output_dir.name,
            "--out", str(report_path),
        ]
        subprocess.run(rep_cmd, check=False)
        _log("report_written", report=str(report_path))

    return proc.returncode


# ─────────────────────────────────────────────────────────────────────────────
# status: show status of recent training output dirs
# ─────────────────────────────────────────────────────────────────────────────

def cmd_status(args: argparse.Namespace) -> int:
    rows = scan_outputs(Path(args.outputs_root), max_age_days=args.max_age_days)
    if not rows:
        print(f"No recent training output dirs found under {args.outputs_root}")
        return 0

    print(f"\n{'='*80}")
    print(f"Training output status: {args.outputs_root}")
    print(f"{'='*80}\n")
    print(f"{'Name':<55} {'Adapter':8} {'Ckpts':6} {'Step':6} {'Modified'}")
    print("-" * 90)
    for row in rows:
        a_mark = "✅ ready" if row["adapter_ready"] else "⏳ ..."
        step   = str(row["latest_checkpoint_step"]) if row["latest_checkpoint_step"] else "—"
        print(
            f"{row['name'][:55]:<55} {a_mark:8} "
            f"{row['n_checkpoints']:6} {step:6} {row['mtime_utc']}"
        )
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# print-eval-cmd: print the harness command to run manually
# ─────────────────────────────────────────────────────────────────────────────

def cmd_print_eval_cmd(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    ts = "$(date +%Y%m%dT%H%M%SZ)"
    eval_out   = output_dir.parent / f"eval-{output_dir.name[:40]}-{ts}.json"
    log_out    = output_dir.parent.parent / "logs" / f"eval-{output_dir.name[:40]}-{ts}.log"

    ascend_prefix = ""
    if args.ascend_devices:
        ascend_prefix = f"ASCEND_VISIBLE_DEVICES={args.ascend_devices} "

    cmd_lines = [
        f"cd {ROOT}",
        f"TS=$(date +%Y%m%dT%H%M%SZ)",
        f"{ascend_prefix}nohup python3 {HARNESS.relative_to(ROOT)} \\",
        f"    --base-model {args.base_model} \\",
        f"    --adapter {output_dir}/adapter \\",
        f"    --output {eval_out} \\",
        f"    --device {args.device} \\",
        f"    --npu-max-memory-gib {args.npu_max_memory_gib} \\",
        f"    --max-new-tokens {args.max_new_tokens} \\",
        f"    --k {args.k} \\",
        f"    --tasks {args.tasks} \\",
        f"    > {log_out} 2>&1 &",
    ]
    print("\n".join(cmd_lines))
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI wiring
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Training-aware eval tracker")
    sub  = root.add_subparsers(dest="cmd", required=True)

    # Shared eval config args
    def _add_eval_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--base-model", required=True)
        p.add_argument("--device", default="npu")
        p.add_argument("--npu-max-memory-gib", type=int, default=50)
        p.add_argument("--max-new-tokens", type=int, default=768)
        p.add_argument("--k", type=int, default=1)
        p.add_argument("--tasks", default="standard12")
        p.add_argument("--eval-file", default=None)

    p_watch = sub.add_parser("watch", help="Poll until adapter ready, then eval")
    p_watch.add_argument("--output-dir", required=True)
    p_watch.add_argument("--eval-output-dir", required=True)
    p_watch.add_argument("--poll-secs", type=int, default=60)
    _add_eval_args(p_watch)

    p_status = sub.add_parser("status", help="Show status of recent training output dirs")
    p_status.add_argument("--outputs-root", required=True)
    p_status.add_argument("--max-age-days", type=int, default=7)

    p_cmd = sub.add_parser("print-eval-cmd", help="Print the harness command to run manually")
    p_cmd.add_argument("--output-dir", required=True)
    p_cmd.add_argument("--ascend-devices", default=None, help="ASCEND_VISIBLE_DEVICES value")
    _add_eval_args(p_cmd)

    return root


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "watch":         cmd_watch,
        "status":        cmd_status,
        "print-eval-cmd": cmd_print_eval_cmd,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())

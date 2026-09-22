#!/usr/bin/env python3
"""checkpoint_publisher.py — ASI3-side producer of the NAS checkpoint bus.

Runs ON ASI3 (installed there; NAS is local). Scans box-local
/vllm-workspace/{run}/step_*_adapter. Each COMPLETED checkpoint
(adapter/adapter_config.json exists) is copied to the shared NAS bus at
/root/work/ckpt_bus/{run}/{step}/ atomically (staged .tmp -> rename), with a
manifest.json (run, step, source, sha16, bytes, published_utc).

Idempotent: a step with an existing manifest is skipped, always.
Eval (ASI2 watcher) polls the bus — eval never again depends on ASI3 daemon
liveness or the daemon transport at all.

Usage (ON ASI3):
    python3 checkpoint_publisher.py --once
    nohup python3 checkpoint_publisher.py --loop &   # 60s cycle
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_config import get  # noqa: E402

BUS = Path(get("ckpt_bus.nas_root"))
TRAIN_ROOT = Path(get("box.training_output_root"))
REPO_NAS = Path(get("box.repo_nas"))
STATE = BUS / "checkpoint_publisher_state.json"   # on NAS: Mac reads it too
POLL_S = 60
COMPLETE = "adapter_config.json"


def _dir_sha16(d: Path) -> str:
    """Content hash of a dir (sorted file hashes). <8 lines."""
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            h.update(f.name.encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def publish_step(step_dir: Path) -> dict:
    """Copy one completed checkpoint (either layout) to the bus, atomically."""
    run, step = _run_step_of(step_dir)
    dest = BUS / run / step
    if (dest / "manifest.json").exists():
        return {"run": run, "step": step, "status": "SKIP_EXISTS"}
    # SFT layout: step_dir IS the adapter dir; GRPO: adapter/ subdir
    adapter_src = step_dir if (step_dir / COMPLETE).exists() else step_dir / "adapter"
    if not (adapter_src / COMPLETE).exists():
        return {"run": run, "step": step, "status": "SKIP_INCOMPLETE"}
    tmp = BUS / f".staging-{run}-{step}"
    subprocess.run(["rm", "-rf", str(tmp)], check=False)
    (tmp / "adapter").mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", str(adapter_src) + "/.", str(tmp / "adapter")], check=True)
    man = {
        "run": run,
        "step": step,
        "source": str(step_dir),
        "sha16": _dir_sha16(tmp / "adapter"),
        "bytes": sum(f.stat().st_size for f in (tmp / "adapter").rglob("*") if f.is_file()),
        "published_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (tmp / "manifest.json").write_text(json.dumps(man) + "\n")
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.rename(tmp, dest)
    return {"run": run, "step": step, "status": "PUBLISHED", "sha16": man["sha16"]}


# Both checkpoint layouts the trainer writes:
#   GRPO (box-local):  /vllm-workspace/{run}/step_NNNNNN_adapter
#   SFT   (NAS repo):  {repo}/outputs/sft-*/checkpoints/step-N/adapter
SCAN_GLOBS = ("*/step_*_adapter", "outputs/sft-*/checkpoints/step-*/adapter")
SFT_RE = None  # compiled lazily


def _run_step_of(step_dir: Path) -> tuple:
    """(run, step) for either layout. <8 lines."""
    import re

    parts = step_dir.parts
    if "checkpoints" in parts:  # SFT layout: .../sft-run/checkpoints/step-N/adapter
        i = parts.index("checkpoints")
        return parts[i - 1], parts[i + 1]
    if step_dir.name == "adapter":  # SFT layout passed with adapter leaf
        return step_dir.parent.parent.name, step_dir.parent.name
    return step_dir.parent.name, step_dir.name  # GRPO layout


def scan_once() -> dict:
    """Scan both checkpoint layouts; publish all completed new steps. <12 lines."""
    results = []
    candidates = []
    for g in SCAN_GLOBS:
        if g.startswith("outputs"):
            candidates += REPO_NAS.glob(g)  # SFT layout lives in the NAS repo
        else:
            candidates += TRAIN_ROOT.glob(g)  # GRPO layout, box-local
    for d in sorted(set(candidates)):
        try:
            r = publish_step(d)
            if r["status"] != "SKIP_INCOMPLETE":
                results.append(r)
        except Exception as exc:  # never kill the loop on one bad step
            run, step = _run_step_of(d)
            results.append({"run": run, "step": step, "status": "ERROR", "error": str(exc)[:200]})
        write_state(results)
    return {"scanned": len(results), "results": results}


def write_state(results: list) -> None:
    """State on NAS for the Mac side. <6 lines."""
    STATE.write_text(
        json.dumps(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "host": os.uname().nodename,
                "published_total": len(results),
                "results": results[-10:],
            },
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    """Dispatch. <10 lines."""
    ap = argparse.ArgumentParser(description="Checkpoint bus publisher (ASI3 side)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    args = ap.parse_args()
    if args.loop:
        while True:
            scan_once()
            time.sleep(POLL_S)
    print(json.dumps(scan_once(), indent=2))


if __name__ == "__main__":
    main()

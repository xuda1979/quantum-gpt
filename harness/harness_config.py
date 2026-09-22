#!/usr/bin/env python3
"""harness_config.py — THE single config for ports, paths, bucket, cadence.

Every script imports from here; nothing re-declares ports or paths.
Change a value here once; all gates/scripts/docs see it.

Usage:
    python3 harness/harness_config.py show
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CONFIG = {
    # Box daemon ports (contract: box_ports_fixed)
    "box_ports": {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653},
    # S3 data path (Mac-side rclone only; boxes cannot reach S3 endpoint)
    "s3": {
        "bucket": "jtdlp-21b4208dde424e96b159362ef49c9c96",
        "endpoint_env": "INER_ENDPOINT",
        "rclone_bin": "/Users/daxu/homebrew/bin/rclone",
    },
    # NAS checkpoint bus (shared /root/work between ASI2 and ASI3)
    "ckpt_bus": {
        "nas_root": "/root/work/ckpt_bus",
        "manifest": "manifest.json",
        "adapter_dir": "adapter",
        "complete_marker": "adapter/adapter_config.json",
    },
    # Box-local paths
    "box": {
        "repo_nas": "/root/work/quantum-gpt",
        "eval_repo": "/root/work/software/quantum-gpt",
        "eval_adapters_dir": "/vllm-workspace/eval_adapters",
        "base_model": "/root/work/filestorage/Qwen3.8-27B",
        "holdout_benchmark": "evals/benchmarks/sapo_promotion_holdout_v1_18.txt",
        "eval_script": "scripts/run_asi2_base_adapter_rubric_eval.py",
        "training_output_root": "/vllm-workspace",
    },
    # Daemon/reconciler cadence
    "cadence": {
        "reconciler_cycle_s": 30,
        "eval_poll_s": 60,
        "auto_launch_poll_s": 10,
        "train_probe_path": "harness/state/probes/train.json",
    },
}


def get(path: str):
    """Dot-path getter: get('box_ports.ASI2') -> 19004."""
    node = CONFIG
    for part in path.split("."):
        node = node[part]
    return node


def main() -> None:
    """Show config. <5 lines."""
    ap = argparse.ArgumentParser(description="Harness single config")
    ap.add_argument("--get", help="dot-path, e.g. box_ports.ASI2")
    args = ap.parse_args()
    if args.get:
        print(json.dumps(get(args.get)))
    else:
        print(json.dumps(CONFIG, indent=2))


if __name__ == "__main__":
    main()

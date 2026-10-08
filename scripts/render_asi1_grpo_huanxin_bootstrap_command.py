#!/usr/bin/env python3
"""Render a single Huanxin command to start ASI1 Qwen3.6-35B-A3B GRPO."""

from __future__ import annotations

import argparse
import base64
import os
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_iner_env() -> dict[str, str]:
    endpoint = os.environ.get("INER_S3_ENDPOINT", "https://iner.aihuanxin.cn")
    access_key = os.environ.get("INER_ACCESS_KEY_ID", "OXF5ar4y")
    bucket = os.environ.get("INER_S3_BUCKET", "jtdlp-21b4208dde424e96b159362ef49c9c96")
    s3_root = os.environ.get("INER_S3_ROOT", f"iner:{bucket}/software/quantum-gpt")
    secret = os.environ.get("INER_SECRET_ACCESS_KEY", "")
    if not secret:
        skill_file = ROOT / "skills" / "iner-s3-transfer" / "SKILL.md"
        if skill_file.exists():
            for line in skill_file.read_text(encoding="utf-8").splitlines():
                prefix = "- Secret access key: `"
                if line.startswith(prefix) and line.endswith("`"):
                    secret = line[len(prefix) : -1]
                    break
    if not secret:
        raise SystemExit(
            "INER_SECRET_ACCESS_KEY is required or must be present in skills/iner-s3-transfer/SKILL.md"
        )
    return {
        "endpoint": endpoint,
        "access_key": access_key,
        "secret": secret,
        "s3_root": s3_root,
    }


def render_command(args: argparse.Namespace) -> str:
    env = load_iner_env()
    config = f"""[iner]
type = s3
provider = Other
access_key_id = {env["access_key"]}
secret_access_key = {env["secret"]}
endpoint = {env["endpoint"]}
acl = private
force_path_style = true
"""
    encoded_config = base64.b64encode(config.encode("utf-8")).decode("ascii")
    lines = [
        "set -euo pipefail",
        "mkdir -p /tmp /workspace/quantum-gpt",
        "python3 - <<'PY'",
        "import base64, pathlib",
        "path = pathlib.Path('/tmp/iner-rclone.conf')",
        f"path.write_bytes(base64.b64decode({encoded_config!r}))",
        "path.chmod(0o600)",
        "PY",
        f"export HUANXIN_GRPO_REMOTE_ROOT={shlex.quote(args.remote_root)}",
        f"export HUANXIN_GRPO_S3_ROOT={shlex.quote(env['s3_root'])}",
        "export HUANXIN_GRPO_RCLONE_CONFIG=/tmp/iner-rclone.conf",
        f"export HUANXIN_GRPO_MODEL_NAME={shlex.quote(args.model_name)}",
        f"export HUANXIN_GRPO_FULL_STEPS={shlex.quote(str(args.full_steps))}",
        f"export HUANXIN_GRPO_CHECKPOINT_INTERVAL_SECONDS={shlex.quote(str(args.checkpoint_interval_seconds))}",
        f"export HUANXIN_GRPO_LORA_RANK={shlex.quote(str(args.lora_rank))}",
        f"export HUANXIN_GRPO_LORA_ALPHA={shlex.quote(str(args.lora_alpha))}",
        f"export HUANXIN_GRPO_MIN_TRAINABLE_PARAMETERS={shlex.quote(str(args.min_trainable_parameters))}",
        f"export HUANXIN_GRPO_MAX_TRAINABLE_PARAMETERS={shlex.quote(str(args.max_trainable_parameters))}",
        "export HUANXIN_GRPO_TARGET_MODULES='q_proj k_proj v_proj o_proj gate_proj up_proj down_proj'",
        "export HUANXIN_GRPO_TRAIN_LAYER_NORM=1",
        "export HUANXIN_GRPO_VISIBLE_DEVICES=0,1,2,3,4,5,6,7",
        "export HUANXIN_GRPO_NPROC_PER_NODE=8",
        "cd /workspace/quantum-gpt",
        "bash scripts/huanxin_pull_and_start_asi1_grpo.sh",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-root", default="/workspace/quantum-gpt")
    parser.add_argument("--model-name", default="/root/work/filestorage/Qwen3.6-35B-A3B")
    parser.add_argument("--full-steps", type=int, default=200000)
    parser.add_argument("--checkpoint-interval-seconds", type=int, default=3600)
    parser.add_argument("--lora-rank", type=int, default=64)
    parser.add_argument("--lora-alpha", type=int, default=128)
    parser.add_argument("--min-trainable-parameters", type=int, default=200_000_000)
    parser.add_argument("--max-trainable-parameters", type=int, default=1_000_000_000)
    parser.add_argument("--output", default="")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    command = render_command(args) + "\n"
    if args.output:
        Path(args.output).write_text(command, encoding="utf-8")
    else:
        print(command, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

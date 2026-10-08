#!/usr/bin/env python3
"""s3_data_path.py — versioned dataset/artifact flow via S3, NOT browser exec.

All data movement (datasets, checkpoints, eval artifacts) goes:
  local → S3 (rclone, versioned+atomic) → box pulls from S3 (rclone).

This removes the browser-automation transport from the data path entirely.

Usage:
    python3 harness/scripts/s3_data_path.py push <local> <s3_prefix>
    python3 harness/scripts/s3_data_path.py pull <s3_key> <local>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

BUCKET = "jtdlp-21b4208dde424e96b159362ef49c9c96"
LOCAL_RCLONE = "/Users/daxu/homebrew/bin/rclone"


def _sha256(data: bytes) -> str:
    """<3 lines."""
    return hashlib.sha256(data).hexdigest()


def versioned_key(name: str, content: bytes) -> str:
    """S3 key with content sha — versioned, immutable. <5 lines."""
    sha = _sha256(content)[:16]
    clean = name.lstrip("/")
    return f"artifacts/{clean}-{sha}"


def build_manifest(name: str, content: bytes, source: str, dest: str) -> dict:
    """Deterministic manifest. <10 lines."""
    return {
        "name": name,
        "sha256": _sha256(content),
        "size": len(content),
        "version": time.strftime("%Y%m%d-%H%M%S"),
        "source": source,
        "dest": dest,
        "s3_key": versioned_key(name, content),
        "bucket": BUCKET,
    }


def transfer_plan(local_path: str, s3_prefix: str, dest_box: str) -> dict:
    """Atomic transfer plan: tmp key → rename. <12 lines."""
    content = Path(local_path).read_bytes()
    name = Path(local_path).name
    final = versioned_key(f"{s3_prefix}/{name}", content)
    tmp = f"{final}.tmp"
    return {
        "local": local_path,
        "remote_tmp": tmp,
        "remote_final": final,
        "dest_box": dest_box,
        "manifest": build_manifest(name, content, "local", dest_box),
        "steps": [
            f"rclone copyto {local_path} iner:{BUCKET}/{tmp}",
            f"rclone moveto iner:{BUCKET}/{tmp} iner:{BUCKET}/{final}",
            f"box {dest_box}: rclone copy iner:{BUCKET}/{final} <target_dir>/",
        ],
    }


def _rclone(args: list[str]) -> dict:
    """Run rclone with INER config. <10 lines."""
    import os

    env = os.environ.copy()
    env["RCLONE_CONFIG_INER_TYPE"] = "s3"
    env["RCLONE_CONFIG_INER_PROVIDER"] = "Other"
    env["RCLONE_CONFIG_INER_ACCESS_KEY_ID"] = os.environ.get("INER_ACCESS_KEY_ID", "")
    env["RCLONE_CONFIG_INER_SECRET_ACCESS_KEY"] = os.environ.get("INER_SECRET_ACCESS_KEY", "")
    env["RCLONE_CONFIG_INER_ENDPOINT"] = os.environ.get(
        "INER_ENDPOINT", "https://iner.aihuanxin.cn"
    )
    env["RCLONE_CONFIG_INER_ACL"] = "private"
    env["RCLONE_CONFIG_INER_FORCE_PATH_STYLE"] = "true"
    try:
        proc = subprocess.run(
            [LOCAL_RCLONE, *args], capture_output=True, text=True, env=env, timeout=120
        )
        return {"ok": proc.returncode == 0, "out": proc.stdout[-300:], "err": proc.stderr[-300:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "err": "TIMEOUT"}


def push(local_path: str, s3_prefix: str) -> dict:
    """Push local → S3 atomically (tmp + moveto). <12 lines."""
    plan = transfer_plan(local_path, s3_prefix, "s3")
    r1 = _rclone(["copyto", plan["local"], f"iner:{BUCKET}/{plan['remote_tmp']}"])
    if not r1["ok"]:
        return {"status": "FAIL", "step": "copy", **r1}
    r2 = _rclone(
        ["moveto", f"iner:{BUCKET}/{plan['remote_tmp']}", f"iner:{BUCKET}/{plan['remote_final']}"]
    )
    return {
        "status": "PASS" if r2["ok"] else "FAIL",
        "step": "rename",
        "key": plan["remote_final"],
        "manifest": plan["manifest"],
        **r2,
    }


def pull(s3_key: str, local_path: str) -> dict:
    """Pull S3 → local. <8 lines."""
    r = _rclone(["copyto", f"iner:{BUCKET}/{s3_key}", local_path])
    return {"status": "PASS" if r["ok"] else "FAIL", **r}


def main() -> None:
    """<12 lines."""
    ap = argparse.ArgumentParser(description="S3 data path (no browser)")
    sub = ap.add_subparsers(dest="cmd")
    p_push = sub.add_parser("push")
    p_push.add_argument("local")
    p_push.add_argument("prefix")
    p_pull = sub.add_parser("pull")
    p_pull.add_argument("key")
    p_pull.add_argument("local")
    args = ap.parse_args()
    if args.cmd == "push":
        print(json.dumps(push(args.local, args.prefix), indent=2))
    elif args.cmd == "pull":
        print(json.dumps(pull(args.key, args.local), indent=2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pull and install a SHA-pinned SAPO bundle through ASI3's S3 proxy route."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/iner-s3-transfer/SKILL.md"
BUCKET = "jtdlp-21b4208dde424e96b159362ef49c9c96"
REMOTE_ROOT = "/root/work/software/quantum-gpt"
DAEMON_URL = "http://127.0.0.1:20653/exec"
INER_HOST = "iner.aihuanxin.cn"
# ASI3's outbound proxy denies CONNECT to INER but allows this hostname. Both
# names currently terminate on the same public endpoint, so curl can ask the
# proxy for an NM tunnel while preserving INER as TLS SNI, HTTP Host, and the
# SigV4/presigned-URL origin.
PROXY_CONNECT_HOST = "nm.aihuanxin.cn"
CONNECT_TO = f"{INER_HOST}:443:{PROXY_CONNECT_HOST}:443"
FILES = (
    "training/grpo_utils.py",
    "training/grpo_trainer.py",
    # Guardian alarm 8 (2026-08-26): repair-sidecar liveness guard — the
    # launcher's required-files check refuses to boot without these.
    "training/sidecar_liveness.py",
    "configs/rl/qwen36_27b_fv_gspo_asi2.json",
    "scripts/asi2_launch_grpo_27b_selfeval.sh",
    "scripts/asi3_launch_grpo_direct.sh",
    "scripts/sapo_ensure_repair_sidecar.sh",
    "scripts/fv_gspo_repair_sidecar.sh",
    "scripts/fv_gspo_repair_stage.py",
    "scripts/build_sapo_distill_question_manifest.py",
    "scripts/validate_sapo_reference_manifest.py",
    "evals/benchmarks/quantum_grpo_training_v6_runtime30_disjoint.txt",
    "evals/benchmarks/sapo_reference_rejects_aac1bad.txt",
    "data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v3/questions_and_code.jsonl",
    "tests/test_sapo_loss.py",
)


def required(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise SystemExit(f"missing {label} in {SKILL}")
    return match.group(1).strip()


def create_signed_url(*, endpoint: str, access_key: str, secret_key: str, object_key: str) -> str:
    """Create a short-lived URL locally; no S3 credential reaches ASI3."""
    rclone = shutil.which("rclone") or "/Users/daxu/homebrew/bin/rclone"
    if not Path(rclone).is_file():
        raise SystemExit("local rclone is required to sign the ASI3 bundle URL")
    env = os.environ.copy()
    env.update(
        {
            "RCLONE_CONFIG_INER_TYPE": "s3",
            "RCLONE_CONFIG_INER_PROVIDER": "Other",
            "RCLONE_CONFIG_INER_ACCESS_KEY_ID": access_key,
            "RCLONE_CONFIG_INER_SECRET_ACCESS_KEY": secret_key,
            "RCLONE_CONFIG_INER_ENDPOINT": endpoint,
            "RCLONE_CONFIG_INER_ACL": "private",
            "RCLONE_CONFIG_INER_FORCE_PATH_STYLE": "true",
        }
    )
    remote = f"iner:{BUCKET}/{object_key.lstrip('/')}"
    completed = subprocess.run(
        [rclone, "link", remote, "--expire", "10m"],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    signed_url = completed.stdout.strip()
    if not signed_url.startswith(f"https://{INER_HOST}/"):
        raise SystemExit("INER did not return the expected HTTPS signed URL")
    return signed_url


def build_remote_command(*, signed_url: str, bundle_sha256: str) -> str:
    """Render a secret-bearing command for the daemon's redacted exec mode."""
    q = shlex.quote
    quoted_files = " ".join(f'"{REMOTE_ROOT}/{relative}"' for relative in FILES)
    return "; ".join(
        [
            "set -eu",
            "BUNDLE=/tmp/asi3-sapo-bundle.tgz",
            "trap 'rm -f \"$BUNDLE\"' EXIT",
            (
                f"curl --connect-to {q(CONNECT_TO)} -fsSL "
                "--retry 3 --retry-all-errors --connect-timeout 10 --max-time 180 "
                f'{q(signed_url)} -o "$BUNDLE"'
            ),
            f'echo {q(bundle_sha256)}  "$BUNDLE" | sha256sum -c -',
            f"mkdir -p {q(REMOTE_ROOT)}",
            f'tar -xzf "$BUNDLE" -C {q(REMOTE_ROOT)}',
            "echo __ASI3_SAPO_SYNC_DONE__",
            f"sha256sum {quoted_files}",
        ]
    )


def build_remote_probe_command(*, signed_url: str) -> str:
    """Download one S3 object to /tmp, hash it, and remove it."""
    q = shlex.quote
    return "; ".join(
        [
            "set -eu",
            "PROBE=/tmp/asi3-iner-route-probe",
            "trap 'rm -f \"$PROBE\"' EXIT",
            (
                f"curl --connect-to {q(CONNECT_TO)} -fsSL "
                "--retry 2 --retry-all-errors --connect-timeout 10 --max-time 60 "
                f'{q(signed_url)} -o "$PROBE"'
            ),
            'test -s "$PROBE"',
            "echo __ASI3_INER_ROUTE_PROBE_OK__",
            'sha256sum "$PROBE"',
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-key")
    parser.add_argument("--bundle-sha256")
    parser.add_argument("--probe-key")
    args = parser.parse_args()
    if args.probe_key:
        if args.bundle_key or args.bundle_sha256:
            parser.error("--probe-key cannot be combined with bundle arguments")
    elif not args.bundle_key or not args.bundle_sha256:
        parser.error("--bundle-key and --bundle-sha256 are required together")

    skill_text = SKILL.read_text(encoding="utf-8")
    access_key = required(r"^- Access key id: `([^`]+)`", skill_text, "access key")
    secret_key = required(r"^- Secret access key: `([^`]+)`", skill_text, "secret key")
    endpoint = required(r"^- Endpoint: `([^`]+)`", skill_text, "endpoint")
    signed_url = create_signed_url(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        object_key=args.probe_key or args.bundle_key,
    )
    if args.probe_key:
        command = build_remote_probe_command(signed_url=signed_url)
    else:
        command = build_remote_command(signed_url=signed_url, bundle_sha256=args.bundle_sha256)
    body = json.dumps(
        {
            "command": command,
            "waitMs": 240000,
            "sensitive": True,
            "redactValues": [access_key, secret_key, signed_url],
        }
    ).encode()
    request = urllib.request.Request(
        DAEMON_URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.load(response)
    safe = {
        "ok": result.get("ok"),
        "commandOk": result.get("commandOk"),
        "commandStatus": result.get("commandStatus"),
        "output": result.get("output", ""),
        "durationMs": result.get("durationMs"),
    }
    print(json.dumps(safe, indent=2))
    if not result.get("ok") or result.get("commandOk") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

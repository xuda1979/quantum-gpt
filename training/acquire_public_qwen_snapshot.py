#!/usr/bin/env python3
"""Acquire and immediately verify a public Qwen snapshot for local->Huanxin handoff.

This helper is intentionally narrow:
- only supports the currently documented public execution checkpoints
- records the chosen model source with the existing audit helper
- downloads a local snapshot with huggingface_hub
- runs the existing offline verifier against the downloaded directory
- can optionally render a branch-specific remote bootstrap command sheet tied to
  the verified local handoff target

It does not push anything to Huanxin. It exists to turn the current
execution-source fork into one auditable local command.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_BOOTSTRAP_BUNDLE = Path("artifacts/huanxin-bootstrap/20260316T143522Z")

PUBLIC_MODELS = {
    "qwen25": {
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "expected_substring": "Qwen2.5-1.5B-Instruct",
        "audit_out": "artifacts/model-source-audit-qwen25.json",
        "handoff_note": "research/qwen25-public-fallback-handoff.md",
        "remote_model_dir": "/root/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct",
        "handoff_manifest": "artifacts/qwen25-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/qwen25-local-snapshot-preflight.json",
    },
    "qwen3-1.7b": {
        "model_id": "Qwen/Qwen3-1.7B",
        "expected_substring": "Qwen3-1.7B",
        "audit_out": "artifacts/model-source-audit-qwen3-1p7b.json",
        "handoff_note": "research/qwen3-public-alternative-handoff.md",
        "remote_model_dir": "/root/root/work/quantum-gpt/models/Qwen3-1.7B",
        "handoff_manifest": "artifacts/qwen3-1p7b-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/qwen3-1p7b-local-snapshot-preflight.json",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        required=True,
        choices=sorted(PUBLIC_MODELS),
        help="Public execution checkpoint to acquire",
    )
    parser.add_argument(
        "--local-dir",
        type=Path,
        help="Optional explicit destination directory for the snapshot",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Optional explicit huggingface_hub cache dir",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only audit and print the planned local/remote handoff metadata without downloading weights",
    )
    parser.add_argument(
        "--render-remote-commands",
        action="store_true",
        help="After successful local acquisition/verification, render a branch-specific Huanxin remote command sheet",
    )
    parser.add_argument(
        "--bootstrap-bundle",
        type=Path,
        default=DEFAULT_BOOTSTRAP_BUNDLE,
        help="Timestamped artifacts/huanxin-bootstrap bundle to render remote commands from",
    )
    parser.add_argument(
        "--hf-timeout-seconds",
        type=float,
        default=30.0,
        help="Timeout passed through to Hugging Face Hub HTTP requests during source audit/download preflight",
    )
    return parser.parse_args()


def run_checked(
    command: list[str],
    *,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(command, check=True, text=True, capture_output=True, env=env)


def render_remote_commands(bundle: Path, remote_model_dir: str) -> tuple[Path, dict]:
    bundle = bundle.resolve()
    output_path = bundle / f"REMOTE_BOOTSTRAP_COMMANDS-{Path(remote_model_dir).name}.sh"
    proc = run_checked(
        [
            sys.executable,
            "scripts/render_huanxin_bootstrap_commands.py",
            str(bundle),
            "--model-name",
            remote_model_dir,
            "--output",
            str(output_path),
        ]
    )
    payload = json.loads(proc.stdout)
    return output_path, payload


def main() -> int:
    args = parse_args()
    spec = PUBLIC_MODELS[args.target]
    model_id = spec["model_id"]
    expected_substring = spec["expected_substring"]
    audit_out = Path(spec["audit_out"])
    handoff_note = spec["handoff_note"]
    remote_model_dir = spec["remote_model_dir"]
    handoff_manifest = Path(spec["handoff_manifest"])
    preflight_manifest = Path(spec["preflight_manifest"])
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    handoff_manifest.parent.mkdir(parents=True, exist_ok=True)
    preflight_manifest.parent.mkdir(parents=True, exist_ok=True)

    hf_env = {
        "HF_HUB_DOWNLOAD_TIMEOUT": str(args.hf_timeout_seconds),
        "HF_HUB_ETAG_TIMEOUT": str(args.hf_timeout_seconds),
    }

    try:
        audit_proc = run_checked(
            [
                sys.executable,
                "training/audit_model_source.py",
                "--model-id",
                model_id,
                "--expected-family-substring",
                "qwen",
                "--out",
                str(audit_out),
                "--timeout-seconds",
                str(args.hf_timeout_seconds),
            ],
            env_overrides=hf_env,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stdout)
        sys.stderr.write(exc.stderr)
        if "timed out" in (exc.stdout + exc.stderr).lower():
            sys.stderr.write(
                f"\nHugging Face source audit timed out for {model_id}. "
                f"This usually means transient metadata/API reachability from this machine, not local code drift. "
                f"Retry later, or use --hf-timeout-seconds > {args.hf_timeout_seconds} if you have reason to believe latency is the only issue.\n"
            )
        return exc.returncode or 1

    audit_summary = json.loads(audit_proc.stdout)

    if args.dry_run:
        result = {
            "status": "dry_run",
            "target": args.target,
            "model_id": model_id,
            "audit_out": str(audit_out),
            "handoff_note": handoff_note,
            "remote_model_dir": remote_model_dir,
            "handoff_manifest": str(handoff_manifest),
            "preflight_manifest": str(preflight_manifest),
            "next_step_hint": f"If this target is approved for execution, rerun without --dry-run and continue with {handoff_note}",
            "audit_summary": audit_summary,
        }
        if args.render_remote_commands:
            try:
                remote_commands_path, render_payload = render_remote_commands(args.bootstrap_bundle, remote_model_dir)
            except subprocess.CalledProcessError as exc:
                sys.stderr.write(exc.stdout)
                sys.stderr.write(exc.stderr)
                return exc.returncode or 1
            result["bootstrap_bundle"] = str(args.bootstrap_bundle.resolve())
            result["remote_commands"] = str(remote_commands_path)
            result["remote_commands_render"] = render_payload
        preflight_manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    py = [
        "from huggingface_hub import snapshot_download",
        "import json",
        f"kwargs = {{'repo_id': {model_id!r}}}",
    ]
    if args.local_dir is not None:
        py.append(f"kwargs['local_dir'] = {str(args.local_dir)!r}")
        py.append("kwargs['local_dir_use_symlinks'] = False")
    if args.cache_dir is not None:
        py.append(f"kwargs['cache_dir'] = {str(args.cache_dir)!r}")
    py.extend(
        [
            "path = snapshot_download(**kwargs)",
            "print(json.dumps({'snapshot_dir': path}))",
        ]
    )

    try:
        download_proc = run_checked([sys.executable, "-c", "\n".join(py)], env_overrides=hf_env)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stdout)
        sys.stderr.write(exc.stderr)
        return exc.returncode or 1

    snapshot_payload = json.loads(download_proc.stdout.strip().splitlines()[-1])
    snapshot_dir = snapshot_payload["snapshot_dir"]

    try:
        verify_proc = run_checked(
            [
                sys.executable,
                "training/verify_qwen_snapshot.py",
                snapshot_dir,
                "--expected-substring",
                expected_substring,
            ]
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stdout)
        sys.stderr.write(exc.stderr)
        return exc.returncode or 1

    verify_summary = json.loads(verify_proc.stdout)
    result = {
        "status": "ok",
        "target": args.target,
        "model_id": model_id,
        "audit_out": str(audit_out),
        "snapshot_dir": snapshot_dir,
        "remote_model_dir": remote_model_dir,
        "handoff_note": handoff_note,
        "handoff_manifest": str(handoff_manifest),
        "next_step_hint": f"If this target is approved for execution, continue with {handoff_note}",
        "verify_summary": verify_summary,
    }
    if args.render_remote_commands:
        try:
            remote_commands_path, render_payload = render_remote_commands(args.bootstrap_bundle, remote_model_dir)
        except subprocess.CalledProcessError as exc:
            sys.stderr.write(exc.stdout)
            sys.stderr.write(exc.stderr)
            return exc.returncode or 1
        result["bootstrap_bundle"] = str(args.bootstrap_bundle.resolve())
        result["remote_commands"] = str(remote_commands_path)
        result["remote_commands_render"] = render_payload
    handoff_manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

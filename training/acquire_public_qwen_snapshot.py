#!/usr/bin/env python3
"""Acquire and immediately verify a public execution-model snapshot for local->Huanxin handoff.

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
DEFAULT_HF_ENDPOINT = "https://huggingface.co"
HF_MIRROR_ENDPOINT = "https://hf-mirror.com"

PUBLIC_MODELS = {
    "qwen36-27b": {
        "model_id": "Qwen/Qwen3.6-27B",
        "expected_substring": "Qwen3.6-27B",
        "expected_family_substring": "qwen",
        "supports_generic_remote_commands": True,
        "audit_out": "artifacts/model-source-audit-qwen36-27b.json",
        "handoff_note": "research/qwen36-27b-handoff.md",
        "remote_model_dir": "/root/software/quantum-gpt/models/Qwen3.6-27B",
        "handoff_manifest": "artifacts/qwen36-27b-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/qwen36-27b-local-snapshot-preflight.json",
    },
    "qwen25": {
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "expected_substring": "Qwen2.5-1.5B-Instruct",
        "expected_family_substring": "qwen",
        "supports_generic_remote_commands": True,
        "audit_out": "artifacts/model-source-audit-qwen25.json",
        "handoff_note": "research/qwen25-public-fallback-handoff.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct",
        "handoff_manifest": "artifacts/qwen25-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/qwen25-local-snapshot-preflight.json",
    },
    "qwen3-1.7b": {
        "model_id": "Qwen/Qwen3-1.7B",
        "expected_substring": "Qwen3-1.7B",
        "expected_family_substring": "qwen",
        "supports_generic_remote_commands": True,
        "audit_out": "artifacts/model-source-audit-qwen3-1p7b.json",
        "handoff_note": "research/qwen3-public-alternative-handoff.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/Qwen3-1.7B",
        "handoff_manifest": "artifacts/qwen3-1p7b-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/qwen3-1p7b-local-snapshot-preflight.json",
    },
    "omnicoder9b": {
        "model_id": "Tesslate/OmniCoder-9B",
        "expected_substring": "OmniCoder-9B",
        "expected_family_substring": "qwen",
        "supports_generic_remote_commands": False,
        "audit_out": "artifacts/model-source-audit-omnicoder9b.json",
        "handoff_note": "research/omnicoder9b-public-handoff.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/OmniCoder-9B",
        "handoff_manifest": "artifacts/omnicoder9b-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/omnicoder9b-local-snapshot-preflight.json",
    },
    "gemma4-e2b-it": {
        "model_id": "google/gemma-4-E2B-it",
        "expected_substring": "gemma-4-E2B-it",
        "expected_family_substring": "gemma",
        "supports_generic_remote_commands": False,
        "audit_out": "artifacts/model-source-audit-gemma4-e2b-it.json",
        "handoff_note": "research/papers/gemma4_text_path_enablement/paper.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/gemma-4-E2B-it",
        "handoff_manifest": "artifacts/gemma4-e2b-it-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/gemma4-e2b-it-local-snapshot-preflight.json",
    },
    "gemma4-e4b-it": {
        "model_id": "google/gemma-4-E4B-it",
        "expected_substring": "gemma-4-E4B-it",
        "expected_family_substring": "gemma",
        "supports_generic_remote_commands": False,
        "audit_out": "artifacts/model-source-audit-gemma4-e4b-it.json",
        "handoff_note": "research/papers/gemma4_text_path_enablement/paper.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/gemma-4-E4B-it",
        "handoff_manifest": "artifacts/gemma4-e4b-it-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/gemma4-e4b-it-local-snapshot-preflight.json",
    },
    "gemma4-26b-a4b-it": {
        "model_id": "google/gemma-4-26B-A4B-it",
        "expected_substring": "gemma-4-26B-A4B-it",
        "expected_family_substring": "gemma",
        "supports_generic_remote_commands": False,
        "audit_out": "artifacts/model-source-audit-gemma4-26b-a4b-it.json",
        "handoff_note": "research/papers/gemma4_text_path_enablement/paper.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/gemma-4-26B-A4B-it",
        "handoff_manifest": "artifacts/gemma4-26b-a4b-it-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/gemma4-26b-a4b-it-local-snapshot-preflight.json",
    },
    "gemma4-31b-it": {
        "model_id": "google/gemma-4-31B-it",
        "expected_substring": "gemma-4-31B-it",
        "expected_family_substring": "gemma",
        "supports_generic_remote_commands": False,
        "audit_out": "artifacts/model-source-audit-gemma4-31b-it.json",
        "handoff_note": "research/papers/gemma4_text_path_enablement/paper.md",
        "remote_model_dir": "/root/work/quantum-gpt/models/gemma-4-31B-it",
        "handoff_manifest": "artifacts/gemma4-31b-it-local-snapshot-handoff.json",
        "preflight_manifest": "artifacts/gemma4-31b-it-local-snapshot-preflight.json",
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
    parser.add_argument(
        "--hf-endpoint",
        help="Optional Hugging Face-compatible endpoint. If omitted, this helper tries the official endpoint first and then hf-mirror.",
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


def build_hf_env(timeout_seconds: float, endpoint: str | None = None) -> dict[str, str]:
    env = {
        "HF_HUB_DOWNLOAD_TIMEOUT": str(int(timeout_seconds)),
        "HF_HUB_ETAG_TIMEOUT": str(int(timeout_seconds)),
    }
    if endpoint:
        env["HF_ENDPOINT"] = endpoint
    return env


def candidate_hf_endpoints(explicit_endpoint: str | None = None) -> list[str]:
    raw_candidates = [
        explicit_endpoint,
        os.environ.get("HF_ENDPOINT"),
        DEFAULT_HF_ENDPOINT,
        HF_MIRROR_ENDPOINT,
    ]
    normalized: list[str] = []
    for endpoint in raw_candidates:
        value = (endpoint or "").strip().rstrip("/")
        if not value or value in normalized:
            continue
        normalized.append(value)
    return normalized


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
    expected_family_substring = spec.get("expected_family_substring", "qwen")
    supports_generic_remote_commands = bool(spec.get("supports_generic_remote_commands", True))
    audit_out = Path(spec["audit_out"])
    handoff_note = spec["handoff_note"]
    remote_model_dir = spec["remote_model_dir"]
    handoff_manifest = Path(spec["handoff_manifest"])
    preflight_manifest = Path(spec["preflight_manifest"])
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    handoff_manifest.parent.mkdir(parents=True, exist_ok=True)
    preflight_manifest.parent.mkdir(parents=True, exist_ok=True)

    audit_summary: dict | None = None
    selected_hf_endpoint: str | None = None
    last_audit_error: subprocess.CalledProcessError | None = None
    for candidate_endpoint in candidate_hf_endpoints(args.hf_endpoint):
        hf_env = build_hf_env(args.hf_timeout_seconds, candidate_endpoint)
        try:
            audit_proc = run_checked(
                [
                    sys.executable,
                    "training/audit_model_source.py",
                    "--model-id",
                    model_id,
                    "--expected-family-substring",
                    expected_family_substring,
                    "--out",
                    str(audit_out),
                    "--timeout-seconds",
                    str(args.hf_timeout_seconds),
                    "--hf-endpoint",
                    candidate_endpoint,
                ],
                env_overrides=hf_env,
            )
            audit_summary = json.loads(audit_proc.stdout)
            selected_hf_endpoint = candidate_endpoint
            break
        except subprocess.CalledProcessError as exc:
            last_audit_error = exc
            combined = (exc.stdout + exc.stderr).lower()
            if "timed out" in combined or "urlerror" in combined:
                continue
            sys.stderr.write(exc.stdout)
            sys.stderr.write(exc.stderr)
            return exc.returncode or 1

    if audit_summary is None or selected_hf_endpoint is None:
        if last_audit_error is not None:
            sys.stderr.write(last_audit_error.stdout)
            sys.stderr.write(last_audit_error.stderr)
        sys.stderr.write(
            f"\nHugging Face source audit failed for {model_id} across endpoints: "
            + ", ".join(candidate_hf_endpoints(args.hf_endpoint))
            + "\n"
        )
        return last_audit_error.returncode if last_audit_error is not None else 1

    if args.dry_run:
        result = {
            "status": "dry_run",
            "target": args.target,
            "model_id": model_id,
            "hf_endpoint": selected_hf_endpoint,
            "audit_out": str(audit_out),
            "handoff_note": handoff_note,
            "remote_model_dir": remote_model_dir,
            "handoff_manifest": str(handoff_manifest),
            "preflight_manifest": str(preflight_manifest),
            "next_step_hint": f"If this target is approved for execution, rerun without --dry-run and continue with {handoff_note}",
            "audit_summary": audit_summary,
        }
        if args.render_remote_commands and supports_generic_remote_commands:
            try:
                remote_commands_path, render_payload = render_remote_commands(
                    args.bootstrap_bundle, remote_model_dir
                )
            except subprocess.CalledProcessError as exc:
                sys.stderr.write(exc.stdout)
                sys.stderr.write(exc.stderr)
                return exc.returncode or 1
            result["bootstrap_bundle"] = str(args.bootstrap_bundle.resolve())
            result["remote_commands"] = str(remote_commands_path)
            result["remote_commands_render"] = render_payload
        elif args.render_remote_commands:
            result["render_remote_commands_warning"] = (
                "Generic remote bootstrap command rendering is disabled for this target because the current "
                "bootstrap path assumes a text-only AutoTokenizer + AutoModelForCausalLM stack. "
                "This target requires a newer runtime and/or a processor-aware conditional-generation path first."
            )
        preflight_manifest.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
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
        download_proc = run_checked(
            [sys.executable, "-c", "\n".join(py)],
            env_overrides=build_hf_env(args.hf_timeout_seconds, selected_hf_endpoint),
        )
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
                "--expected-family-substring",
                expected_family_substring,
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
        "hf_endpoint": selected_hf_endpoint,
        "audit_out": str(audit_out),
        "snapshot_dir": snapshot_dir,
        "remote_model_dir": remote_model_dir,
        "handoff_note": handoff_note,
        "handoff_manifest": str(handoff_manifest),
        "next_step_hint": f"If this target is approved for execution, continue with {handoff_note}",
        "verify_summary": verify_summary,
    }
    if args.render_remote_commands and supports_generic_remote_commands:
        try:
            remote_commands_path, render_payload = render_remote_commands(
                args.bootstrap_bundle, remote_model_dir
            )
        except subprocess.CalledProcessError as exc:
            sys.stderr.write(exc.stdout)
            sys.stderr.write(exc.stderr)
            return exc.returncode or 1
        result["bootstrap_bundle"] = str(args.bootstrap_bundle.resolve())
        result["remote_commands"] = str(remote_commands_path)
        result["remote_commands_render"] = render_payload
    elif args.render_remote_commands:
        result["render_remote_commands_warning"] = (
            "Generic remote bootstrap command rendering is disabled for this target because the current "
            "bootstrap path assumes a text-only AutoTokenizer + AutoModelForCausalLM stack. "
            f"{Path(remote_model_dir).name} requires a newer Transformers runtime and a processor-aware path first."
        )
    handoff_manifest.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

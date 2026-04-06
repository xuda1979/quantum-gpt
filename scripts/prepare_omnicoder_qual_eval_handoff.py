#!/usr/bin/env python3
"""Prepare an audited OmniCoder qualitative-eval handoff artifact.

This script does not perform any network transfer. It packages the exact local
inputs, hashes, and next commands for the blocked S3 -> ai2 qualitative eval so
the handoff is ready the moment the outer approval layer allows transfer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = ROOT / "artifacts" / "deliveries"
DEFAULT_BASE_MODEL = Path("models/OmniCoder-9B")
DEFAULT_ADAPTER = Path("outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter")
DEFAULT_SLICE = Path("reports/base_vs_adapter_eval_slice_interface_prefix.json")
DEFAULT_REPORT = Path("reports/base_vs_adapter_outputs_omnicoder9b_semantic_v4_true20.json")
DEFAULT_LOG = Path("/tmp/base-vs-adapter-omnicoder9b-semantic-v4-true20.log")
DEFAULT_DELIVERY_MANIFEST = Path("artifacts/deliveries/omnicoder9b_first_working_adapter_20260330.json")
SCRIPT_INPUTS = [
    Path("scripts/run_base_vs_adapter_eval.py"),
    Path("scripts/summarize_base_vs_adapter_report.py"),
    Path("training/qwen_sft_peft.py"),
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_path(path: Path, *, expect_dir: bool | None = None) -> None:
    if not path.exists():
        raise SystemExit(f"Required path not found: {path}")
    if expect_dir is True and not path.is_dir():
        raise SystemExit(f"Expected directory, found file: {path}")
    if expect_dir is False and not path.is_file():
        raise SystemExit(f"Expected file, found directory: {path}")


def collect_file_record(path: Path) -> dict[str, Any]:
    require_path(path, expect_dir=False)
    rel_path = path.relative_to(ROOT)
    return {
        "path": str(rel_path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_json(path: Path) -> dict[str, Any]:
    require_path(path, expect_dir=False)
    return json.loads(path.read_text(encoding="utf-8"))


def build_commands(
    push_paths: list[str],
    report_path: str,
    log_path: str,
    base_model: str,
    adapter_path: str,
    slice_path: str,
) -> dict[str, str]:
    joined_push_paths = " ".join(push_paths)
    eval_cmd = (
        "cd /root/root/work/quantum-gpt && "
        "nohup env PYTHONPYCACHEPREFIX=/tmp/pycache TOKENIZERS_PARALLELISM=false "
        "python3 scripts/run_base_vs_adapter_eval.py "
        f"--slice-json {slice_path} "
        f"--base-model {base_model} "
        f"--adapter {adapter_path} "
        f"--output {report_path} "
        "--device npu --limit 5 --max-new-tokens 128 "
        f"> {log_path} 2>&1 < /dev/null &"
    )
    return {
        "push_to_s3": f"./scripts/push_to_s3.sh {joined_push_paths}",
        "sync_ai2_from_s3": "./scripts/ai2_sync_from_s3.sh",
        "launch_eval_on_ai2": f"./scripts/ai2_shell.sh \"{eval_cmd}\"",
        "watch_report": (
            "./scripts/watch_base_vs_adapter_report.sh "
            f"ai2 {report_path} {report_path} {log_path}"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", type=Path, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--slice-json", type=Path, default=DEFAULT_SLICE)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--delivery-manifest", type=Path, default=DEFAULT_DELIVERY_MANIFEST)
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUT_ROOT,
        help="Directory under which the timestamped handoff artifact is created.",
    )
    parser.add_argument(
        "--label",
        default="omnicoder9b-qual-eval-handoff",
        help="Short label embedded in the emitted handoff metadata.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_model = (ROOT / args.base_model).resolve()
    adapter = (ROOT / args.adapter).resolve()
    slice_json = (ROOT / args.slice_json).resolve()
    delivery_manifest_path = (ROOT / args.delivery_manifest).resolve()

    require_path(base_model, expect_dir=True)
    require_path(adapter, expect_dir=True)
    require_path(slice_json, expect_dir=False)

    script_records = [collect_file_record(ROOT / rel_path) for rel_path in SCRIPT_INPUTS]
    slice_record = collect_file_record(slice_json)
    delivery_manifest = load_json(delivery_manifest_path)
    adapter_readme = adapter / "README.md"
    adapter_readme_record = collect_file_record(adapter_readme)

    artifact_dir = args.out_root / f"{args.label}_{utc_stamp()}"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    push_paths = [record["path"] for record in script_records]
    push_paths.append(slice_record["path"])

    commands = build_commands(
        push_paths=push_paths,
        report_path=str(args.report_path),
        log_path=str(args.log_path),
        base_model=str(args.base_model),
        adapter_path=str(args.adapter),
        slice_path=str(args.slice_json),
    )

    handoff_manifest = {
        "label": args.label,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(ROOT),
        "blocker": {
            "type": "outer-approval-layer",
            "summary": "Direct networked file transfer remains blocked outside the workspace.",
            "blocked_command": "/Users/daxu/homebrew/bin/rclone copy scripts/run_base_vs_adapter_eval.py \"nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/scripts\" --s3-no-check-bucket --progress",
        },
        "base_model": str(args.base_model),
        "adapter": {
            "path": str(args.adapter),
            "readme": adapter_readme_record,
            "delivery_manifest": delivery_manifest,
        },
        "eval_slice": slice_record,
        "script_inputs": script_records,
        "commands": commands,
    }

    manifest_path = artifact_dir / "handoff_manifest.json"
    commands_path = artifact_dir / "NEXT_ACTIONS.sh"
    manifest_path.write_text(json.dumps(handoff_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    commands_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        "# This file is intentionally non-executing by default because the required\n"
        "# network transfer is blocked by the outer approval layer in the current agent.\n\n"
        f"# 1. Push exact local changes to S3\n{commands['push_to_s3']}\n\n"
        f"# 2. Sync the ai2 workspace from S3\n{commands['sync_ai2_from_s3']}\n\n"
        f"# 3. Launch the OmniCoder qualitative eval on ai2\n{commands['launch_eval_on_ai2']}\n\n"
        f"# 4. Watch and fetch the report once it appears\n{commands['watch_report']}\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "artifact_dir": str(artifact_dir),
                "manifest": str(manifest_path),
                "commands": str(commands_path),
                "push_paths": push_paths,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
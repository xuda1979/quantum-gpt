#!/usr/bin/env python3
"""Prepare a minimal validated bootstrap bundle for Huanxin remote fine-tuning.

This script intentionally packages only the smallest set of files needed to
recreate the next remote step inside `/root/root/work/quantum-gpt`.

Workflow:
1. Confirm required local artifacts exist.
2. Copy only the requested validated files into a timestamped bundle dir.
3. Emit a shell script with the exact remote commands to recreate the bundle.
4. Emit a manifest for auditing what was transferred.

The bundle is text-first so it can be pasted or mirrored through the Huanxin
surface without relying on S3 or rsync.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = ROOT / "artifacts" / "huanxin-bootstrap"
REMOTE_ROOT = "/root/root/work/quantum-gpt"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_text(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise SystemExit(f"Required file not found: {path}")


def copy_files(paths: list[Path], bundle_root: Path) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for src in paths:
        require_file(src)
        rel = src.relative_to(ROOT)
        dest = bundle_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        copied.append(
            {
                "path": str(rel),
                "bytes": src.stat().st_size,
                "sha256": sha256_text(src),
            }
        )
    return copied


def build_remote_commands(files: list[dict[str, Any]]) -> str:
    lines = [
        "set -euo pipefail",
        f"mkdir -p {REMOTE_ROOT}",
        f"cd {REMOTE_ROOT}",
        "",
        "# Create required directories before pasting file contents.",
    ]
    dirs = sorted({str(Path(item['path']).parent) for item in files if str(Path(item['path']).parent) != "."})
    for rel_dir in dirs:
        lines.append(f"mkdir -p {rel_dir}")

    lines.extend(
        [
            "",
            "# Paste each file from the local bundle into the matching remote path.",
            "# Example pattern:",
            "# cat > relative/path.py <<'EOF'",
            "# ...paste validated file contents...",
            "# EOF",
            "",
            "# After pasting files, run the baseline local-equivalent gate where possible:",
            "python3 evals/runner/run_eval.py",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        help="Workspace-relative file paths to include in the remote bootstrap bundle.",
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUT_ROOT,
        help="Directory under which timestamped bundles are created.",
    )
    parser.add_argument(
        "--label",
        default="manual",
        help="Short label included in the bundle manifest.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src_paths = [(ROOT / rel).resolve() for rel in args.paths]
    bundle_root = args.out_root / utc_stamp()
    bundle_root.mkdir(parents=True, exist_ok=True)

    copied = copy_files(src_paths, bundle_root)
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "workspace_root": str(ROOT),
        "remote_root": REMOTE_ROOT,
        "files": copied,
    }
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (bundle_root / "REMOTE_COMMANDS.sh").write_text(build_remote_commands(copied))

    print(json.dumps({
        "bundle_root": str(bundle_root),
        "file_count": len(copied),
        "manifest": str(bundle_root / 'manifest.json'),
        "remote_commands": str(bundle_root / 'REMOTE_COMMANDS.sh'),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

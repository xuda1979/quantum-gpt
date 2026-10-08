#!/usr/bin/env python3
"""Build a reproducible delivery tarball from a machine-readable manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_size_human(num_bytes: int) -> str:
    units = ["B", "K", "M", "G", "T"]
    value = float(num_bytes)
    unit = units[0]
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            break
        value /= 1024.0
    if unit == "B":
        return f"{int(value)}{unit}"
    if value >= 100:
        return f"{value:.0f}{unit}"
    if value >= 10:
        return f"{value:.1f}{unit}"
    return f"{value:.2f}{unit}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to a delivery manifest JSON file.")
    parser.add_argument(
        "--rewrite-manifest",
        action="store_true",
        help="Rewrite the manifest with the newly built artifact sha256 and size_human.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate packaging prerequisites without emitting a tarball.",
    )
    return parser.parse_args()


def require_path(path: Path, *, expect_dir: bool | None = None) -> None:
    if not path.exists():
        raise SystemExit(f"Required path not found: {path}")
    if expect_dir is True and not path.is_dir():
        raise SystemExit(f"Expected directory, found file: {path}")
    if expect_dir is False and not path.is_file():
        raise SystemExit(f"Expected file, found directory: {path}")


def find_adapter_weight(adapter_dir: Path) -> Path:
    for candidate in ("adapter_model.safetensors", "adapter_model.bin"):
        path = adapter_dir / candidate
        if path.exists():
            return path
    raise SystemExit(
        "Delivery artifact cannot be built because the adapter directory does not contain "
        f"`adapter_model.safetensors` or `adapter_model.bin`: {adapter_dir}"
    )


def collect_members(root: Path, payload: dict[str, Any]) -> list[Path]:
    adapter_dir = (root / str(payload.get("adapter_dir") or "")).resolve()
    metrics_file = (root / str(payload.get("metrics_file") or "")).resolve()
    report_file = (root / str(payload.get("report_file") or "")).resolve()
    artifact_path = (root / str(payload.get("artifact") or "")).resolve()

    require_path(adapter_dir, expect_dir=True)
    require_path(metrics_file, expect_dir=False)
    require_path(report_file, expect_dir=False)
    find_adapter_weight(adapter_dir)

    members = [adapter_dir, metrics_file, report_file]
    run_config = metrics_file.parent / "run_config.json"
    if run_config.exists():
        members.append(run_config)

    extra_paths = payload.get("extra_paths") or []
    for extra in extra_paths:
        extra_path = (root / str(extra)).resolve()
        require_path(extra_path)
        members.append(extra_path)

    # Avoid accidentally archiving the artifact into itself.
    return [member for member in members if member != artifact_path]


def build_tarball(root: Path, artifact_path: Path, members: list[Path]) -> None:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(artifact_path, "w:gz") as tar:
        for member in members:
            arcname = member.relative_to(root)
            tar.add(member, arcname=str(arcname), recursive=True)


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    root = manifest_path.parents[2]
    payload = load_json(manifest_path)
    artifact_path = (root / str(payload.get("artifact") or "")).resolve()
    if not str(payload.get("artifact") or "").endswith(".tar.gz"):
        raise SystemExit(f"Delivery artifact must end with .tar.gz: {payload.get('artifact')}")

    members = collect_members(root, payload)
    if args.check_only:
        print(
            json.dumps(
                {
                    "manifest": str(manifest_path),
                    "artifact": str(artifact_path),
                    "member_count": len(members),
                    "members": [str(member.relative_to(root)) for member in members],
                    "ok": True,
                },
                indent=2,
            )
        )
        return 0

    build_tarball(root, artifact_path, members)
    size_bytes = artifact_path.stat().st_size
    artifact_sha256 = sha256_file(artifact_path)
    if args.rewrite_manifest:
        payload["sha256"] = artifact_sha256
        payload["size_human"] = format_size_human(size_bytes)
        manifest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "artifact": str(artifact_path),
                "sha256": artifact_sha256,
                "size_human": format_size_human(size_bytes),
                "member_count": len(members),
                "members": [str(member.relative_to(root)) for member in members],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

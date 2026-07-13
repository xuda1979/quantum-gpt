#!/usr/bin/env python3
"""Audit the model registry so trained models cannot silently go untracked or lost.

The model registry (``artifacts/model-registry/index.json`` plus one
``<output-dir>.json`` archive per run) is the source of truth for "what have we
trained and where does it live". This doctor turns the previously *silent*
failure modes into a loud, actionable report and a non-zero exit code so the
registry can be gated in automation:

Problems detected
  * unarchived_local_run   -- a completed run exists under outputs/ locally
                              (metrics.json present) but is missing from the
                              registry index.
  * index_archive_missing  -- an index entry points at a per-run archive file
                              that does not exist or does not parse.
  * weights_unreachable    -- an archived run has neither a local adapter dir
                              nor any recorded storage location, so the trained
                              weights cannot be located at all.
  * no_offsite_backup      -- an archived run's weights are reachable but only
                              on a single non-backed-up location (no s3/oss/etc.),
                              i.e. one disk failure from being lost.

Usage:
  python3 scripts/model_registry_doctor.py            # human report, exit 1 on problems
  python3 scripts/model_registry_doctor.py --json      # machine-readable report
  python3 scripts/model_registry_doctor.py --warn-only # always exit 0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "artifacts" / "model-registry"
INDEX_PATH = REGISTRY_DIR / "index.json"
OUTPUTS_DIR = ROOT / "outputs"

OFFSITE_KINDS = {"s3", "oss", "gcs", "iner", "minio", "azure", "b2"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def try_load_json(path: Path) -> Any | None:
    try:
        return load_json(path)
    except Exception:
        return None


def storage_summary(archive: dict[str, Any], index_entry: dict[str, Any]) -> dict[str, Any]:
    """Resolve reachability + offsite-backup from archive storage or index hints."""
    storage = archive.get("storage") if isinstance(archive, dict) else None
    if not isinstance(storage, dict):
        storage = {}
    locations = storage.get("locations")
    if not isinstance(locations, list):
        locations = index_entry.get("storage_locations")
    if not isinstance(locations, list):
        locations = []
    kinds = {str(loc.get("kind", "")).lower() for loc in locations if isinstance(loc, dict)}
    local_adapter_exists = bool(storage.get("local_adapter_exists"))
    # Fall back to the on-disk output_dir adapter if the archive predates the
    # storage block.
    output_dir = index_entry.get("output_dir") or archive.get("output_dir")
    if output_dir:
        adapter = ROOT / str(output_dir) / "adapter"
        if adapter.exists():
            local_adapter_exists = True
    reachable = bool(locations) or local_adapter_exists or bool(storage.get("weights_reachable"))
    offsite = (
        bool(storage.get("offsite_backup"))
        or bool(kinds & OFFSITE_KINDS)
        or bool(index_entry.get("offsite_backup"))
    )
    return {
        "locations": locations,
        "local_adapter_exists": local_adapter_exists,
        "weights_reachable": reachable,
        "offsite_backup": offsite,
    }


def audit() -> dict[str, Any]:
    problems: list[dict[str, Any]] = []
    runs_report: list[dict[str, Any]] = []

    if not INDEX_PATH.exists():
        problems.append({"kind": "index_missing", "path": str(INDEX_PATH.relative_to(ROOT))})
        return {"problems": problems, "runs": runs_report, "archived_output_dirs": []}

    index = load_json(INDEX_PATH)
    index_runs = index.get("runs", []) if isinstance(index, dict) else []
    archived_output_dirs = {str(r.get("output_dir")) for r in index_runs if isinstance(r, dict)}

    for entry in index_runs:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label")
        archive_path_str = entry.get("archive_path")
        archive: dict[str, Any] = {}
        if isinstance(archive_path_str, str):
            archive_payload = try_load_json(ROOT / archive_path_str)
            if archive_payload is None:
                problems.append(
                    {
                        "kind": "index_archive_missing",
                        "label": label,
                        "archive_path": archive_path_str,
                    }
                )
            elif isinstance(archive_payload, dict):
                archive = archive_payload
        summary = storage_summary(archive, entry)
        if not summary["weights_reachable"]:
            problems.append({"kind": "weights_unreachable", "label": label})
        elif not summary["offsite_backup"]:
            problems.append({"kind": "no_offsite_backup", "label": label})
        runs_report.append(
            {
                "label": label,
                "output_dir": entry.get("output_dir"),
                "base_model": entry.get("base_model"),
                "weights_reachable": summary["weights_reachable"],
                "offsite_backup": summary["offsite_backup"],
                "local_adapter_exists": summary["local_adapter_exists"],
                "storage_locations": summary["locations"],
            }
        )

    # Local completed runs not yet archived.
    if OUTPUTS_DIR.exists():
        for run_dir in sorted(OUTPUTS_DIR.glob("*")):
            if not run_dir.is_dir():
                continue
            if not (run_dir / "metrics.json").exists():
                continue
            rel = f"outputs/{run_dir.name}"
            if rel not in archived_output_dirs and str(run_dir) not in archived_output_dirs:
                problems.append({"kind": "unarchived_local_run", "output_dir": rel})

    return {
        "problems": problems,
        "runs": runs_report,
        "archived_output_dirs": sorted(archived_output_dirs),
    }


def format_human(report: dict[str, Any]) -> str:
    lines: list[str] = []
    runs = report["runs"]
    lines.append(f"Model registry: {len(runs)} archived run(s)")
    for r in runs:
        flags = []
        flags.append("reachable" if r["weights_reachable"] else "UNREACHABLE")
        flags.append("backed-up" if r["offsite_backup"] else "no-offsite-backup")
        loc = (
            ", ".join(f"{l.get('kind')}:{l.get('uri')}" for l in r["storage_locations"])
            or "(no storage recorded)"
        )
        lines.append(f"  - {r['label']}")
        lines.append(f"      base={r['base_model']}  [{' | '.join(flags)}]")
        lines.append(f"      weights: {loc}")
    problems = report["problems"]
    if not problems:
        lines.append("\nOK: no registry problems detected.")
    else:
        lines.append(f"\n{len(problems)} problem(s) detected:")
        for p in problems:
            kind = p.get("kind")
            ident = p.get("label") or p.get("output_dir") or p.get("path") or ""
            lines.append(f"  [{kind}] {ident}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report.")
    p.add_argument(
        "--warn-only", action="store_true", help="Always exit 0 even when problems are found."
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_human(report))
    if report["problems"] and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

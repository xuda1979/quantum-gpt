#!/usr/bin/env python3
"""Diff two dataset snapshots at file + row granularity.

The lightweight, air-gapped DVC-diff replacement. Compares two snapshots
produced by scripts/dataset_version.py and reports:
  - manifest field changes (added/removed/changed keys, with old vs new)
  - per-file changes (added / removed / modified, with byte-size delta)
  - for JSONL files: row-level diff (added rows, removed rows, changed rows)
    using the per-row sha256 lists stored in the snapshot
  - aggregate row counts (train/eval delta)

Usage
-----
  # Diff two snapshot files directly
  python3 scripts/dataset_diff.py artifacts/dataset-registry/A@....json artifacts/dataset-registry/B@....json

  # Diff two dataset versions by name + version index (0 = newest)
  python3 scripts/dataset_diff.py --dataset glm52_soft_distill_sft_iter2 --versions 1,0

  # Diff two live dataset dirs (snapshots them in-memory, no write)
  python3 scripts/dataset_diff.py --dir data/generated/A data/generated/B
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO / "artifacts" / "dataset-registry"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_versioning_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "dataset_version", REPO / "scripts" / "dataset_version.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# Diff components
# ─────────────────────────────────────────────────────────────────────────────


def _diff_manifest(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Diff the manifest extracts of two snapshots."""
    if not a and not b:
        return {}
    keys = sorted(set(a) | set(b))
    changes: list[dict[str, Any]] = []
    for k in keys:
        va, vb = a.get(k), b.get(k)
        if k not in a:
            changes.append({"key": k, "change": "added", "new": vb})
        elif k not in b:
            changes.append({"key": k, "change": "removed", "old": va})
        elif va != vb:
            changes.append({"key": k, "change": "changed", "old": va, "new": vb})
    return {"field_changes": changes, "n_changes": len(changes)}


def _files_map(snap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {f["path"]: f for f in snap.get("files", [])}


def _diff_files(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Diff the file lists of two snapshots."""
    fa, fb = _files_map(a), _files_map(b)
    paths = sorted(set(fa) | set(fb))
    added, removed, modified = [], [], []
    for p in paths:
        if p not in fa:
            added.append({"path": p, "bytes": fb[p]["bytes"], "sha256": fb[p]["sha256"][:12]})
        elif p not in fb:
            removed.append({"path": p, "bytes": fa[p]["bytes"], "sha256": fa[p]["sha256"][:12]})
        elif fa[p]["sha256"] != fb[p]["sha256"]:
            modified.append(
                {
                    "path": p,
                    "bytes_old": fa[p]["bytes"],
                    "bytes_new": fb[p]["bytes"],
                    "bytes_delta": fb[p]["bytes"] - fa[p]["bytes"],
                    "sha256_old": fa[p]["sha256"][:12],
                    "sha256_new": fb[p]["sha256"][:12],
                    "row_count_old": fa[p].get("row_count"),
                    "row_count_new": fb[p].get("row_count"),
                    "row_delta": (fb[p].get("row_count", 0) - fa[p].get("row_count", 0))
                    if fa[p].get("row_count") is not None and fb[p].get("row_count") is not None
                    else None,
                }
            )
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "n_added": len(added),
        "n_removed": len(removed),
        "n_modified": len(modified),
    }


def _diff_jsonl_rows(file_a: dict[str, Any], file_b: dict[str, Any]) -> dict[str, Any]:
    """Row-level diff for a JSONL file present (possibly modified) in both snapshots."""
    ra = {r["i"]: r["sha256"] for r in file_a.get("row_hashes", [])}
    rb = {r["i"]: r["sha256"] for r in file_b.get("row_hashes", [])}
    # Rows are indexed by line number. Identify:
    #   - rows present in both with same hash → unchanged
    #   - rows present in both with different hash → changed
    #   - rows only in A (index < len(A)) → removed
    #   - rows only in B (index >= len(A)) → added
    # This is a positional diff (line-number keyed), not an LCS diff. It's
    # cheap and unambiguous for append-only datasets, which is the common
    # case for this project (iter-N+1 carries forward iter-N rows + adds new).
    idx_a = set(ra)
    idx_b = set(rb)
    common = idx_a & idx_b
    changed_idx = [i for i in sorted(common) if ra[i] != rb[i]]
    removed_idx = sorted(idx_a - idx_b)
    added_idx = sorted(idx_b - idx_a)
    return {
        "rows_unchanged": len(common) - len(changed_idx),
        "rows_changed": len(changed_idx),
        "rows_added": len(added_idx),
        "rows_removed": len(removed_idx),
        "changed_indices": changed_idx[:20],  # cap for readability
        "added_indices_first": added_idx[:20],
        "removed_indices_last": removed_idx[-20:] if removed_idx else [],
    }


def _diff_rows(
    a: dict[str, Any], b: dict[str, Any], modified_files: list[dict[str, Any]]
) -> dict[str, Any]:
    """Row-level diff across all modified JSONL files."""
    fa = _files_map(a)
    fb = _files_map(b)
    per_file: list[dict[str, Any]] = []
    for mf in modified_files:
        p = mf["path"]
        file_a, file_b = fa[p], fb[p]
        if "row_hashes" not in file_a or "row_hashes" not in file_b:
            continue
        per_file.append(
            {
                "path": p,
                **_diff_jsonl_rows(file_a, file_b),
            }
        )
    return {"jsonl_files": per_file}


def diff_snapshots(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Full diff between two dataset snapshots."""
    files_diff = _diff_files(a, b)
    modified_files = files_diff["modified"]
    rows_diff = _diff_rows(a, b, modified_files)
    return {
        "diff_schema_version": 1,
        "a": {
            "dataset": a.get("dataset"),
            "content_hash": a.get("content_hash"),
            "snapshot_at_utc": a.get("snapshot_at_utc"),
        },
        "b": {
            "dataset": b.get("dataset"),
            "content_hash": b.get("content_hash"),
            "snapshot_at_utc": b.get("snapshot_at_utc"),
        },
        "manifest_diff": _diff_manifest(a.get("manifest") or {}, b.get("manifest") or {}),
        "files_diff": files_diff,
        "rows_diff": rows_diff,
        "summary": {
            "files_added": files_diff["n_added"],
            "files_removed": files_diff["n_removed"],
            "files_modified": files_diff["n_modified"],
            "manifest_fields_changed": len(
                _diff_manifest(a.get("manifest") or {}, b.get("manifest") or {}).get(
                    "field_changes", []
                )
            ),
            "total_bytes_delta": b.get("total_bytes", 0) - a.get("total_bytes", 0),
            "total_rows_delta": b.get("row_count_total", 0) - a.get("row_count_total", 0),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Renderers
# ─────────────────────────────────────────────────────────────────────────────


def render_human(diff: dict[str, Any]) -> str:
    a, b = diff["a"], diff["b"]
    s = diff["summary"]
    lines = []
    lines.append(f"\nDataset diff: {a.get('dataset','?')} -> {b.get('dataset','?')}")
    lines.append(f"  A: {a.get('content_hash','?')[:12]}  ({a.get('snapshot_at_utc','?')[:19]})")
    lines.append(f"  B: {b.get('content_hash','?')[:12]}  ({b.get('snapshot_at_utc','?')[:19]})")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"  files: +{s['files_added']} -{s['files_removed']} ~{s['files_modified']}")
    lines.append(f"  manifest fields changed: {s['manifest_fields_changed']}")
    lines.append(f"  total bytes delta: {s['total_bytes_delta']:+d}")
    lines.append(f"  total rows delta: {s['total_rows_delta']:+d}")

    # Manifest changes
    md = diff["manifest_diff"]
    if md.get("field_changes"):
        lines.append("\nManifest field changes:")
        for c in md["field_changes"]:
            if c["change"] == "added":
                lines.append(f"  + {c['key']}: {json.dumps(c['new'], ensure_ascii=False)[:60]}")
            elif c["change"] == "removed":
                lines.append(f"  - {c['key']}: {json.dumps(c['old'], ensure_ascii=False)[:60]}")
            else:
                lines.append(
                    f"  ~ {c['key']}: {json.dumps(c['old'], ensure_ascii=False)[:40]} -> {json.dumps(c['new'], ensure_ascii=False)[:40]}"
                )

    # File changes
    fd = diff["files_diff"]
    if fd["added"]:
        lines.append("\nFiles added:")
        for f in fd["added"]:
            lines.append(f"  + {f['path']}  ({f['bytes']} B, sha {f['sha256']})")
    if fd["removed"]:
        lines.append("\nFiles removed:")
        for f in fd["removed"]:
            lines.append(f"  - {f['path']}  ({f['bytes']} B, sha {f['sha256']})")
    if fd["modified"]:
        lines.append("\nFiles modified:")
        for f in fd["modified"]:
            rd = (
                f"  rows {f['row_count_old']} -> {f['row_count_new']} ({f['row_delta']:+d})"
                if f.get("row_delta") is not None
                else ""
            )
            lines.append(
                f"  ~ {f['path']}  ({f['bytes_old']} -> {f['bytes_new']} B, {f['bytes_delta']:+d}){rd}"
            )

    # Row-level diff
    rd = diff["rows_diff"]
    if rd["jsonl_files"]:
        lines.append("\nRow-level diff (positional, line-number keyed):")
        for f in rd["jsonl_files"]:
            lines.append(f"  {f['path']}:")
            lines.append(
                f"    unchanged: {f['rows_unchanged']}  changed: {f['rows_changed']}  +added: {f['rows_added']}  -removed: {f['rows_removed']}"
            )
            if f["rows_changed"]:
                lines.append(f"    changed row indices (first 20): {f['changed_indices']}")
            if f["rows_added"]:
                lines.append(f"    added row indices (first 20): {f['added_indices_first']}")
            if f["rows_removed"]:
                lines.append(f"    removed row indices (last 20): {f['removed_indices_last']}")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Resolvers
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_by_versions(dataset: str, versions: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve two snapshots by dataset name + comma-separated version indices (0=newest)."""
    index = _load_json(REGISTRY_DIR / "index.json") or {"datasets": {}}
    versions_list = index.get("datasets", {}).get(dataset, [])
    if not versions_list:
        raise FileNotFoundError(f"no snapshots for dataset '{dataset}'")
    ia, ib = (int(x) for x in versions.split(","))
    if ia >= len(versions_list) or ib >= len(versions_list):
        raise IndexError(f"version index out of range (have {len(versions_list)} snapshots)")
    sa = _load_json(REGISTRY_DIR / versions_list[ia]["snapshot_file"])
    sb = _load_json(REGISTRY_DIR / versions_list[ib]["snapshot_file"])
    if sa is None or sb is None:
        raise FileNotFoundError("snapshot file missing on disk")
    return sa, sb


def _resolve_by_dirs(dir_a: Path, dir_b: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Snapshot two live dirs in-memory and diff."""
    dv = _load_versioning_module()
    sa = dv.snapshot_dataset(dir_a)
    sb = dv.snapshot_dataset(dir_b)
    return sa, sb


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("snap_a", nargs="?", help="Snapshot file A (or omit and use --dataset/--dir)")
    p.add_argument("snap_b", nargs="?", help="Snapshot file B (or omit and use --dataset/--dir)")
    p.add_argument("--dataset", help="Dataset name (use with --versions)")
    p.add_argument("--versions", help="Comma-separated version indices, e.g. 1,0 (0=newest)")
    p.add_argument("--dir", nargs=2, metavar=("DIR_A", "DIR_B"), help="Diff two live dataset dirs")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable")
    args = p.parse_args()

    if args.dir:
        sa, sb = _resolve_by_dirs(Path(args.dir[0]), Path(args.dir[1]))
    elif args.dataset and args.versions:
        sa, sb = _resolve_by_versions(args.dataset, args.versions)
    elif args.snap_a and args.snap_b:
        sa = _load_json(Path(args.snap_a))
        sb = _load_json(Path(args.snap_b))
        if sa is None or sb is None:
            print("ERROR: could not load snapshot file(s)", file=sys.stderr)
            return 2
    else:
        p.error("provide two snapshot files, or --dataset + --versions, or --dir A B")
        return 2

    diff = diff_snapshots(sa, sb)
    if args.json:
        print(json.dumps(diff, indent=2, ensure_ascii=False))
    else:
        print(render_human(diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

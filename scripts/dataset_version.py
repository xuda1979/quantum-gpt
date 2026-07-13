#!/usr/bin/env python3
"""Content-addressed dataset versioning — the lightweight, air-gapped
DVC replacement, tailored to this project's manifest conventions.

What it does
------------
For a dataset directory (e.g. data/generated/glm52_soft_distill_sft_iter2/):
  1. Hashes every file (sha256).
  2. Reads the dataset's manifest.json if present (preserves source_sha256,
     train_out/eval_out, split_method, iteration, status, gap_topic_counts,
     composition_target, etc.).
  3. For JSONL data files, computes a per-row hash list so two versions can
     be diffed at row granularity (added / removed / changed rows) without
     re-reading the full file.
  4. Writes a snapshot record into artifacts/dataset-registry/<dataset>.json
     and appends to artifacts/dataset-registry/index.json.
  5. Records git SHA at snapshot time.

This gives us DVC's core value (immutable, content-addressed dataset
versions with a queryable index) without DVC's remote-storage/cachedir
machinery, which doesn't fit our air-gapped NPU + S3-relay workflow.

Usage
-----
  # Snapshot one dataset
  python3 scripts/dataset_version.py snapshot data/generated/glm52_soft_distill_sft_iter2

  # Snapshot all datasets under a root
  python3 scripts/dataset_version.py snapshot --all data/generated/

  # List all registered dataset versions
  python3 scripts/dataset_version.py list

  # Show one dataset's version history
  python3 scripts/dataset_version.py history glm52_soft_distill_sft_iter2

  # Look up which dataset version a training run used (by train_file path)
  python3 scripts/dataset_version.py lookup data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO / "artifacts" / "dataset-registry"
INDEX_PATH = REGISTRY_DIR / "index.json"

# Manifest fields worth preserving in the snapshot (best effort — anything
# present is kept, anything absent is omitted).
MANIFEST_PRESERVE_FIELDS = (
    "source_sha256",
    "source_file",
    "source_size_bytes",
    "distillation_model",
    "teacher_target",
    "system_prompt",
    "split_method",
    "train_out",
    "eval_out",
    "train_rows",
    "eval_rows",
    "eos_marker_stripped",
    "notes",
    "iteration",
    "created",
    "status",
    "base_source",
    "supplement_source",
    "gap_report_source",
    "gap_topic_counts",
    "composition_target",
    "recommended_tracks",
    "quality_gates",
    "decision_gates",
)


# ─────────────────────────────────────────────────────────────────────────────
# Hashing helpers
# ─────────────────────────────────────────────────────────────────────────────


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _git_sha() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _row_hashes(jsonl_path: Path) -> list[dict[str, Any]]:
    """Compute per-row hashes for a JSONL file.

    Returns a list of {row_index, sha256, line_len} dicts. The row hash is
    over the raw line text (not parsed JSON) so malformed-but-stable rows
    still hash deterministically.
    """
    rows: list[dict[str, Any]] = []
    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f):
            line = line.rstrip("\n")
            rows.append(
                {
                    "i": idx,
                    "sha256": _sha256_str(line),
                    "len": len(line),
                }
            )
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot
# ─────────────────────────────────────────────────────────────────────────────


def snapshot_dataset(ds_dir: Path, *, note: str | None = None) -> dict[str, Any]:
    """Build a snapshot record for one dataset directory."""
    ds_dir = ds_dir.resolve()
    if not ds_dir.is_dir():
        raise FileNotFoundError(f"dataset dir not found: {ds_dir}")

    name = ds_dir.name
    files: list[dict[str, Any]] = []
    for p in sorted(ds_dir.rglob("*")):
        if p.is_file() and not p.name.startswith("."):
            rel = str(p.relative_to(ds_dir))
            entry: dict[str, Any] = {
                "path": rel,
                "bytes": p.stat().st_size,
                "sha256": _sha256_file(p),
            }
            if p.suffix == ".jsonl":
                entry["row_count"] = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
                entry["row_hashes"] = _row_hashes(p)
            files.append(entry)

    # Dataset-level content hash: sha256 of the sorted (path, sha256) tuples.
    files_sorted = sorted(files, key=lambda f: f["path"])
    content_hash_input = "\n".join(f"{f['path']}:{f['sha256']}" for f in files_sorted)
    content_hash = _sha256_str(content_hash_input)

    # Manifest
    manifest = _load_json(ds_dir / "manifest.json") or {}
    manifest_extract = {k: manifest[k] for k in MANIFEST_PRESERVE_FIELDS if k in manifest}

    snapshot = {
        "dataset": name,
        "snapshot_schema_version": 1,
        "snapshot_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha_at_snapshot": _git_sha(),
        "dataset_dir": str(ds_dir.relative_to(REPO))
        if ds_dir.is_relative_to(REPO)
        else str(ds_dir),
        "content_hash": content_hash,
        "file_count": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "row_count_total": sum(f.get("row_count", 0) for f in files),
        "files": files_sorted,
        "manifest": manifest_extract,
        "note": note,
    }
    return snapshot


def _write_snapshot(snapshot: dict[str, Any]) -> Path:
    """Write a snapshot to artifacts/dataset-registry/<dataset>.json and
    append a pointer to artifacts/dataset-registry/index.json."""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    ds_name = snapshot["dataset"]
    content_hash = snapshot["content_hash"][:12]
    ts = snapshot["snapshot_at_utc"].replace(":", "").replace("-", "")[:15]
    snap_file = REGISTRY_DIR / f"{ds_name}@{ts}-{content_hash}.json"
    snap_file.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Update index
    index = _load_json(INDEX_PATH) or {"archive_version": "dataset-registry-v1", "datasets": {}}
    if "datasets" not in index:
        index["datasets"] = {}
    entry = {
        "dataset": ds_name,
        "content_hash": snapshot["content_hash"],
        "snapshot_at_utc": snapshot["snapshot_at_utc"],
        "snapshot_file": snap_file.name,
        "git_sha_at_snapshot": snapshot["git_sha_at_snapshot"],
        "file_count": snapshot["file_count"],
        "total_bytes": snapshot["total_bytes"],
        "row_count_total": snapshot["row_count_total"],
        "train_rows": snapshot["manifest"].get("train_out")
        or snapshot["manifest"].get("train_rows"),
        "eval_rows": snapshot["manifest"].get("eval_out") or snapshot["manifest"].get("eval_rows"),
        "note": snapshot.get("note"),
    }
    ds_list = index["datasets"].setdefault(ds_name, [])
    # Replace any prior entry with the same content_hash
    ds_list[:] = [e for e in ds_list if e["content_hash"] != entry["content_hash"]]
    ds_list.append(entry)
    # Keep newest first
    ds_list.sort(key=lambda e: e["snapshot_at_utc"], reverse=True)
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snap_file


# ─────────────────────────────────────────────────────────────────────────────
# Index / history / lookup
# ─────────────────────────────────────────────────────────────────────────────


def load_index() -> dict[str, Any]:
    return _load_json(INDEX_PATH) or {"archive_version": "dataset-registry-v1", "datasets": {}}


def cmd_list(args: argparse.Namespace) -> int:
    index = load_index()
    datasets = index.get("datasets", {})
    if not datasets:
        print("(no datasets registered yet)")
        return 0
    print(
        f"\n{'Dataset':45s} {'versions':>8s} {'latest_content_hash':>13s}  {'latest_snapshot':>20s}  rows"
    )
    print("-" * 110)
    for name in sorted(datasets):
        versions = datasets[name]
        latest = versions[0]
        ch = latest["content_hash"][:12]
        ts = latest["snapshot_at_utc"][:19].replace("T", " ")
        rows = latest.get("row_count_total", 0)
        print(f"{name:45s} {len(versions):>8d} {ch:>13s}  {ts:>20s}  {rows}")
    print(f"\n{sum(len(v) for v in datasets.values())} snapshots across {len(datasets)} datasets")
    print(f"Index: {INDEX_PATH.relative_to(REPO)}")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    index = load_index()
    versions = index.get("datasets", {}).get(args.dataset, [])
    if not versions:
        print(f"(no snapshots for dataset '{args.dataset}')", file=sys.stderr)
        return 1
    print(f"\nHistory for {args.dataset} ({len(versions)} snapshots)\n")
    for v in versions:
        ch = v["content_hash"][:12]
        ts = v["snapshot_at_utc"][:19].replace("T", " ")
        tr = v.get("train_rows")
        er = v.get("eval_rows")
        rows = v.get("row_count_total", 0)
        note = f"  note: {v['note']}" if v.get("note") else ""
        rows_str = f"train={tr} eval={er}" if tr is not None or er is not None else f"rows={rows}"
        print(f"  {ts}  {ch}  {rows_str}  files={v['file_count']}{note}")
        print(f"    snapshot: artifacts/dataset-registry/{v['snapshot_file']}")
    return 0


def cmd_lookup(args: argparse.Namespace) -> int:
    """Look up which dataset version(s) contain a given file path."""
    target = Path(args.path).resolve()
    index = load_index()
    datasets = index.get("datasets", {})
    hits: list[tuple[str, dict[str, Any]]] = []
    for name, versions in datasets.items():
        for v in versions:
            snap = _load_json(REGISTRY_DIR / v["snapshot_file"])
            if not snap:
                continue
            for f in snap.get("files", []):
                # Resolve the file path relative to repo
                candidate = (REPO / snap["dataset_dir"] / f["path"]).resolve()
                if candidate == target:
                    hits.append((name, v))
                    break
    if not hits:
        print(f"(no snapshot contains {target})", file=sys.stderr)
        return 1
    print(f"\n{len(hits)} snapshot(s) contain {target}:\n")
    for name, v in hits:
        ts = v["snapshot_at_utc"][:19].replace("T", " ")
        ch = v["content_hash"][:12]
        print(f"  {name:40s} {ts}  {ch}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot CLI
# ─────────────────────────────────────────────────────────────────────────────


def cmd_snapshot(args: argparse.Namespace) -> int:
    if args.all:
        root = Path(args.dataset_or_root).resolve()
        if not root.is_dir():
            print(f"ERROR: root not found: {root}", file=sys.stderr)
            return 2
        n = 0
        for d in sorted(root.iterdir()):
            if d.is_dir() and not d.name.startswith("_") and not d.name.startswith("."):
                if (d / "manifest.json").exists() or any(d.glob("*.jsonl")):
                    try:
                        snap = snapshot_dataset(d, note=args.note)
                        out = _write_snapshot(snap)
                        print(f"snapshot {d.name} -> {out.name}")
                        n += 1
                    except Exception as e:
                        print(f"ERROR {d.name}: {e}", file=sys.stderr)
        print(f"\n{n} datasets snapshotted")
        return 0
    # Single dataset
    ds_dir = Path(args.dataset_or_root).resolve()
    snap = snapshot_dataset(ds_dir, note=args.note)
    out = _write_snapshot(snap)
    print(f"snapshot {snap['dataset']} -> {out.name}")
    print(f"  content_hash: {snap['content_hash']}")
    print(
        f"  files: {snap['file_count']}  bytes: {snap['total_bytes']}  rows: {snap['row_count_total']}"
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("snapshot", help="Snapshot a dataset (or --all under a root)")
    ps.add_argument("dataset_or_root", help="Dataset dir, or root dir if --all")
    ps.add_argument(
        "--all", action="store_true", help="Snapshot every dataset dir under the given root"
    )
    ps.add_argument("--note", help="Optional note for this snapshot")
    ps.set_defaults(func=cmd_snapshot)
    pl = sub.add_parser("list", help="List all registered dataset versions")
    pl.set_defaults(func=cmd_list)
    ph = sub.add_parser("history", help="Show version history for one dataset")
    ph.add_argument("dataset", help="Dataset name (dir basename)")
    ph.set_defaults(func=cmd_history)
    pk = sub.add_parser("lookup", help="Find which dataset version(s) contain a file path")
    pk.add_argument("path", help="File path to look up")
    pk.set_defaults(func=cmd_lookup)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

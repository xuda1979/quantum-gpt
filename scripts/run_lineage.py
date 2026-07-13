#!/usr/bin/env python3
"""Stitch per-run artifacts into a single lineage JSON.

For a given training output directory (containing run_config.json +
metrics.json) this script produces a `lineage.json` that captures:

  - run identity (output dir, environment, timestamps, git SHA if available)
  - model + adapter init provenance
  - dataset provenance (train/eval file paths + sha256 from the dataset
    manifest if one exists alongside or in data/generated/<name>/manifest.json)
  - training hyperparameters (from run_config.json)
  - final metrics (loss, perplexity, completed_steps from metrics.json)
  - linked eval results (any eval-*.json or scorecard.json under evals/runs/
    whose name references the run, plus any in the run dir itself)
  - artifact hashes (sha256 of run_config.json, metrics.json, and the
    adapter weights if present)

This is the lightweight, air-gapped alternative to W&B Artifacts: every
run becomes a self-describing JSON blob that can be diffed and compared
without any external service.

Usage:
  python3 scripts/run_lineage.py --run-dir outputs/qwen36-27b-...-20260528T122221Z
  python3 scripts/run_lineage.py --run-dir outputs/... --write          # writes lineage.json into the run dir
  python3 scripts/run_lineage.py --scan outputs/                        # scan all run dirs, write lineage.json where missing
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


def _repo_root_for(run_dir: Path) -> Path:
    """Resolve the repo root for a given run dir.

    Prefers the CWD if it looks like a repo root (contains run_config.json's
    parent chain under it), otherwise falls back to the script's repo.
    This allows the script to work both in the real repo and in test fixtures
    that create a synthetic repo root.
    """
    cwd = Path.cwd()
    # If the run dir is under the CWD, treat CWD as the repo root.
    try:
        run_dir.relative_to(cwd)
        return cwd
    except ValueError:
        pass
    return REPO


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_sha() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_dataset_manifest(train_file: str | None) -> dict[str, Any] | None:
    """Locate a manifest.json for a dataset path.

    Looks in:
      1. <dataset_dir>/manifest.json
      2. data/generated/<basename>/manifest.json
      3. data/generated/<basename without _train/_eval suffix>/manifest.json
    """
    if not train_file:
        return None
    p = Path(train_file)
    # Direct manifest alongside
    candidates = [p.parent / "manifest.json"]
    # If the path is something/NAME_train.jsonl, look for something/manifest.json
    name = p.stem
    for suffix in ("_train", "_eval", "_sft", "_chatml"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            candidates.append(p.parent / f"{name}" / "manifest.json")
            break
    # data/generated/<dir>/manifest.json
    if "data/generated" in str(p):
        candidates.append(p.parent / "manifest.json")
    for c in candidates:
        m = _load_json(c)
        if m:
            return m
    return None


def _lookup_dataset_version(repo: Path, dataset_dir: Path) -> dict[str, Any] | None:
    """Look up the registered dataset version (content_hash + snapshot file)
    from artifacts/dataset-registry/index.json, matching by dataset dir name."""
    idx_path = repo / "artifacts" / "dataset-registry" / "index.json"
    idx = _load_json(idx_path)
    if not idx:
        return None
    datasets = idx.get("datasets", {})
    name = dataset_dir.name
    versions = datasets.get(name, [])
    if not versions:
        return None
    latest = versions[0]  # newest first
    return {
        "dataset_name": name,
        "content_hash": latest["content_hash"],
        "snapshot_file": latest["snapshot_file"],
        "snapshot_at_utc": latest["snapshot_at_utc"],
        "registered_train_rows": latest.get("train_rows"),
        "registered_eval_rows": latest.get("eval_rows"),
    }


def _find_adapter(run_dir: Path) -> Path | None:
    """Find adapter weights under a run dir."""
    adapter_dir = run_dir / "adapter"
    if adapter_dir.is_dir():
        # Look for adapter_model.safetensors or adapter_config.json
        for name in ("adapter_model.safetensors", "adapter_config.json"):
            if (adapter_dir / name).exists():
                return adapter_dir
    # Sometimes the adapter is directly under the run dir
    for name in ("adapter_model.safetensors", "adapter_config.json"):
        if (run_dir / name).exists():
            return run_dir
    return None


def _find_linked_evals(run_dir: Path, run_name: str) -> list[dict[str, Any]]:
    """Find eval results linked to this run.

    Looks for:
      1. eval-*.json or scorecard.json inside the run dir
      2. evals/runs/<run_name>*/eval-*.json or scorecard.json
      3. evals/runs/*/<run_name>*eval*.json (any eval referencing the run name)
    """
    repo = _repo_root_for(run_dir)
    evals: list[dict[str, Any]] = []
    seen: set[Path] = set()

    def _add_eval(path: Path) -> None:
        ap = path.resolve()
        if ap in seen or not ap.exists():
            return
        seen.add(ap)
        data = _load_json(ap)
        if data is None:
            return
        # Extract pass summary
        summary = _extract_eval_summary(data)
        evals.append(
            {
                "path": str(ap.relative_to(repo)) if ap.is_relative_to(repo) else str(ap),
                "sha256": _sha256_file(ap),
                "schema_version": data.get("schema_version"),
                "created_at_utc": data.get("created_at_utc") or data.get("scored_at_utc"),
                **summary,
            }
        )

    # 1. Inside run dir
    for pat in ("eval-*.json", "scorecard.json", "*eval*.json"):
        for p in run_dir.glob(pat):
            _add_eval(p)

    # 2 & 3. Under evals/runs/
    evals_runs = repo / "evals" / "runs"
    if evals_runs.is_dir():
        # Direct match by run name
        for d in evals_runs.iterdir():
            if d.name.startswith(run_name) or run_name.startswith(d.name):
                for pat in ("eval-*.json", "scorecard.json"):
                    for p in d.glob(pat):
                        _add_eval(p)
        # Any eval file referencing the run name
        for p in evals_runs.rglob("*.json"):
            name = p.name.lower()
            if run_name.lower() in name and ("eval" in name or "scorecard" in name):
                _add_eval(p)

    return evals


def _extract_eval_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Extract a pass@1 summary from either v1 scorecard or v2 harness output."""
    # v2: results keyed by model -> summary
    if data.get("schema_version", 1) >= 2:
        results = data.get("results", {})
        out: dict[str, Any] = {"models": {}}
        for mk, mv in results.items():
            s = mv.get("summary", {})
            out["models"][mk] = {
                "pass_at_1": s.get("pass_at_1"),
                "n_tasks": s.get("n_tasks"),
                "n_pass": s.get("n_pass"),
            }
        return out
    # v1 scorecard: results is a list of records with `passed`
    results = data.get("results")
    if isinstance(results, list):
        n = len(results)
        n_pass = sum(1 for r in results if r.get("passed") or r.get("pass_at_1", 0) > 0)
        return {
            "pass_at_1": round(n_pass / n, 4) if n else 0.0,
            "n_tasks": n,
            "n_pass": n_pass,
        }
    # v1 records list
    records = data.get("records")
    if isinstance(records, list):
        n = len(records)
        n_pass = sum(1 for r in records if r.get("passed") or r.get("pass_at_1", 0) > 0)
        return {
            "pass_at_1": round(n_pass / n, 4) if n else 0.0,
            "n_tasks": n,
            "n_pass": n_pass,
        }
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────────────────────────────────────


def build_lineage(run_dir: Path) -> dict[str, Any]:
    """Build a lineage dict for a single run directory."""
    run_dir = run_dir.resolve()
    repo = _repo_root_for(run_dir)
    run_name = run_dir.name
    run_config = _load_json(run_dir / "run_config.json") or {}
    metrics = _load_json(run_dir / "metrics.json") or {}

    # Dataset provenance
    train_file = run_config.get("train_file") or run_config.get("signature", {}).get("train_file")
    eval_file = run_config.get("eval_file") or run_config.get("signature", {}).get("eval_file")
    dataset_manifest = _find_dataset_manifest(train_file)

    # Adapter
    adapter_path = _find_adapter(run_dir)

    # Linked evals
    linked_evals = _find_linked_evals(run_dir, run_name)

    # Git SHA at lineage-build time (best effort; may differ from run time)
    git_sha = _git_sha()

    lineage = {
        "lineage_schema_version": 1,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_name": run_name,
        "run_dir": str(run_dir.relative_to(repo)) if run_dir.is_relative_to(repo) else str(run_dir),
        "git_sha_at_build": git_sha,
        "run_identity": {
            "environment": run_config.get("environment"),
            "huanxin_task_id": run_config.get("huanxin_task_id"),
            "huanxin_task_name": run_config.get("huanxin_task_name"),
            "generated_at_utc": run_config.get("generated_at_utc"),
            "remote_output_dir": run_config.get("remote_output_dir"),
            "submit_time": run_config.get("submit_time"),
            "task_start_time": run_config.get("task_start_time"),
            "task_end_time": run_config.get("task_end_time"),
            "task_status_code": run_config.get("task_status_code"),
            "task_status_text": run_config.get("task_status_text"),
        },
        "model": {
            "model_name": run_config.get("model_name")
            or run_config.get("signature", {}).get("model_name"),
            "adapter_init": run_config.get("adapter_init")
            or run_config.get("signature", {}).get("adapter_init"),
        },
        "dataset": {
            "train_file": train_file,
            "eval_file": eval_file,
            "manifest": dataset_manifest,
            "registered_version": (
                _lookup_dataset_version(repo, Path(train_file).parent) if train_file else None
            ),
        },
        "hyperparameters": run_config.get("signature")
        or {
            k: v
            for k, v in run_config.items()
            if k
            in {
                "max_length",
                "per_device_batch_size",
                "gradient_accumulation_steps",
                "learning_rate",
                "num_epochs",
                "max_steps",
                "eval_steps",
                "log_steps",
                "lora_rank",
                "lora_alpha",
                "lora_dropout",
                "lora_backend",
                "train_layernorm",
                "max_trainable_parameters",
                "load_in_8bit",
                "benchmark_file",
                "online_eval_benchmark_file",
                "grpo_steps",
                "group_size",
                "max_new_tokens",
                "max_turns",
                "training_mode",
                "world_size",
                "nproc_per_node",
                "visible_devices",
            }
        },
        "metrics": {
            "completed_steps": metrics.get("completed_steps"),
            "max_steps": metrics.get("max_steps"),
            "train_examples": metrics.get("train_examples"),
            "eval_examples": metrics.get("eval_examples"),
            "final_eval": metrics.get("final_eval"),
            "world_size": metrics.get("world_size"),
        }
        if metrics
        else None,
        "adapter": {
            "path": str(adapter_path.relative_to(repo))
            if adapter_path and adapter_path.is_relative_to(repo)
            else (str(adapter_path) if adapter_path else None),
            "exists": adapter_path is not None,
        },
        "linked_evals": linked_evals,
        "artifact_hashes": {
            "run_config.json": _sha256_file(run_dir / "run_config.json"),
            "metrics.json": _sha256_file(run_dir / "metrics.json"),
        },
    }
    return lineage


def cmd_build(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"ERROR: run dir not found: {run_dir}", file=sys.stderr)
        return 2
    lineage = build_lineage(run_dir)
    if args.write:
        out = run_dir / "lineage.json"
        out.write_text(json.dumps(lineage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(json.dumps(lineage, indent=2, ensure_ascii=False))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.scan).resolve()
    if not root.is_dir():
        print(f"ERROR: scan root not found: {root}", file=sys.stderr)
        return 2
    n_written = 0
    n_skipped = 0
    n_errors = 0
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if not (d / "run_config.json").exists():
            continue
        out = d / "lineage.json"
        if out.exists() and not args.force:
            n_skipped += 1
            continue
        try:
            lineage = build_lineage(d)
            out.write_text(
                json.dumps(lineage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            n_written += 1
            print(f"wrote {out}")
        except Exception as e:
            n_errors += 1
            print(f"ERROR {d}: {e}", file=sys.stderr)
    print(f"\nscan complete: {n_written} written, {n_skipped} skipped, {n_errors} errors")
    return 0 if n_errors == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    pb = sub.add_parser("build", help="Build lineage.json for one run dir")
    pb.add_argument("--run-dir", required=True)
    pb.add_argument("--write", action="store_true", help="Write lineage.json into the run dir")
    pb.set_defaults(func=cmd_build)
    ps = sub.add_parser(
        "scan", help="Scan a directory of run dirs, writing lineage.json where missing"
    )
    ps.add_argument("scan", help="Root directory to scan (e.g. outputs/)")
    ps.add_argument("--force", action="store_true", help="Overwrite existing lineage.json")
    ps.set_defaults(func=cmd_scan)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

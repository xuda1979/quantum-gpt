#!/usr/bin/env python3
"""Compare multiple training runs from their lineage.json (or run_config.json).

Produces a compact table view of run identity, dataset, key hyperparameters,
final metrics, and linked eval pass@1 — the lightweight, air-gapped
alternative to a W&B runs table.

Usage:
  # Compare specific runs (by lineage.json or run dir)
  python3 scripts/compare_runs.py outputs/run-A/lineage.json outputs/run-B/lineage.json

  # Compare all runs under a directory (auto-discovers lineage.json or run_config.json)
  python3 scripts/compare_runs.py --dir outputs/

  # JSON output for downstream tooling
  python3 scripts/compare_runs.py --dir outputs/ --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]

# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_lineage(path: Path) -> dict[str, Any]:
    """Load a lineage.json, or build one on-the-fly from a run dir."""
    path = path.resolve()
    if path.is_file() and path.name == "lineage.json":
        return _load_json(path) or {}
    # If it's a run dir (or a run_config.json), import the builder
    if path.is_dir():
        run_dir = path
    elif path.is_file() and path.name in ("run_config.json", "metrics.json"):
        run_dir = path.parent
    else:
        raise FileNotFoundError(f"not a lineage.json or run dir: {path}")
    # Try existing lineage.json first
    existing = run_dir / "lineage.json"
    if existing.exists():
        return _load_json(existing) or {}
    # Build on the fly
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_lineage", REPO / "scripts" / "run_lineage.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_lineage(run_dir)


def discover_runs(root: Path) -> list[Path]:
    """Find all run dirs under root that have run_config.json or lineage.json."""
    runs: list[Path] = []
    if not root.is_dir():
        return runs
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if (d / "lineage.json").exists() or (d / "run_config.json").exists():
            runs.append(d)
    return runs


# ─────────────────────────────────────────────────────────────────────────────
# Extractors
# ─────────────────────────────────────────────────────────────────────────────


def _short(s: str | None, width: int = 28) -> str:
    if not s:
        return "—"
    s = str(s)
    if len(s) <= width:
        return s
    return s[: width - 1] + "…"


def _eval_pass_summary(linked_evals: list[dict[str, Any]]) -> str:
    if not linked_evals:
        return "—"
    parts: list[str] = []
    for ev in linked_evals:
        # v2 multi-model
        models = ev.get("models")
        if models:
            for mk, mv in models.items():
                p = mv.get("pass_at_1")
                n = mv.get("n_tasks")
                if p is not None:
                    parts.append(f"{mk}:{p:.0%}({n})")
        else:
            p = ev.get("pass_at_1")
            n = ev.get("n_tasks")
            if p is not None:
                parts.append(f"{p:.0%}({n})")
    return ", ".join(parts) if parts else "—"


def _metric_summary(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return "—"
    fe = metrics.get("final_eval") or {}
    loss = fe.get("loss")
    ppl = fe.get("perplexity")
    steps = metrics.get("completed_steps")
    s = ""
    if loss is not None:
        s += f"loss={loss:.4f}"
    if ppl is not None:
        s += f"  ppl={ppl:.3f}"
    if steps is not None:
        s += f"  steps={steps}"
    return s or "—"


def _hp_summary(hp: dict[str, Any]) -> str:
    if not hp:
        return "—"
    parts: list[str] = []
    for key in ("lora_rank", "lora_alpha", "learning_rate", "num_epochs", "max_steps"):
        v = hp.get(key)
        if v is not None:
            parts.append(f"{key}={v}")
    return " ".join(parts) if parts else "—"


def _dataset_summary(dataset: dict[str, Any]) -> str:
    if not dataset:
        return "—"
    tf = dataset.get("train_file")
    mf = dataset.get("manifest") or {}
    if mf:
        train_rows = mf.get("train_out") or mf.get("train_rows") or mf.get("train")
        eval_rows = mf.get("eval_out") or mf.get("eval_rows") or mf.get("eval")
        if isinstance(train_rows, int) and isinstance(eval_rows, int):
            return f"{train_rows}+{eval_rows}"
    return _short(tf, 24) if tf else "—"


# ─────────────────────────────────────────────────────────────────────────────
# Table renderer
# ─────────────────────────────────────────────────────────────────────────────

COLUMNS = [
    ("run", 44, lambda r: _short(r.get("run_name"), 43)),
    ("env", 6, lambda r: r.get("run_identity", {}).get("environment") or "—"),
    ("dataset", 18, lambda r: _dataset_summary(r.get("dataset") or {})),
    ("hp", 44, lambda r: _short(_hp_summary(r.get("hyperparameters") or {}), 43)),
    ("metrics", 30, lambda r: _short(_metric_summary(r.get("metrics")), 29)),
    ("eval@1", 26, lambda r: _short(_eval_pass_summary(r.get("linked_evals") or []), 25)),
    ("adapter", 6, lambda r: "yes" if (r.get("adapter") or {}).get("exists") else "—"),
]


def render_table(rows: list[dict[str, Any]]) -> str:
    header = "  ".join(name.ljust(width) for name, width, _ in COLUMNS)
    sep = "  ".join("-" * width for _, width, _ in COLUMNS)
    lines = [header, sep]
    for r in rows:
        lines.append("  ".join(fn(r).ljust(width) for _, width, fn in COLUMNS))
    return "\n".join(lines)


def render_json(rows: list[dict[str, Any]]) -> str:
    # Compact JSON with only the comparison-relevant fields
    out = []
    for r in rows:
        out.append(
            {
                "run_name": r.get("run_name"),
                "environment": r.get("run_identity", {}).get("environment"),
                "dataset": _dataset_summary(r.get("dataset") or {}),
                "hyperparameters": r.get("hyperparameters"),
                "metrics": r.get("metrics"),
                "linked_evals": r.get("linked_evals"),
                "adapter_exists": (r.get("adapter") or {}).get("exists"),
                "git_sha_at_build": r.get("git_sha_at_build"),
            }
        )
    return json.dumps(out, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("paths", nargs="*", help="lineage.json files or run dirs to compare")
    p.add_argument("--dir", help="Discover all runs under this directory")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = p.parse_args()

    targets: list[Path] = [Path(x) for x in args.paths]
    if args.dir:
        targets.extend(discover_runs(Path(args.dir)))
    if not targets:
        p.error("no runs specified: provide paths or --dir")

    rows: list[dict[str, Any]] = []
    for t in targets:
        try:
            lineage = load_lineage(t)
            if lineage:
                rows.append(lineage)
        except Exception as e:
            print(f"WARNING: skip {t}: {e}", file=sys.stderr)

    if not rows:
        print("No runs found.", file=sys.stderr)
        return 1

    if args.json:
        print(render_json(rows))
    else:
        print(f"\n{len(rows)} runs compared\n")
        print(render_table(rows))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

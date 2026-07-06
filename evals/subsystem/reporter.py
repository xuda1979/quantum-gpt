#!/usr/bin/env python3
"""Generate human-readable Markdown and machine-readable JSON reports.

Consolidates multiple eval runs (across iterations, models, environments) into
a single structured report suitable for:
  - The daily R&D status brief
  - Feeding into the next dataset curation step
  - Tracking progress across training iterations

Usage:
  # Single-run Markdown report:
  python3 evals/subsystem/reporter.py single \\
      --eval outputs/eval-35b-glm52-distill-iter2-pass1-12task.json \\
      --out reports/eval_iter2_35b.md

  # Multi-run trend table comparing multiple eval JSON files:
  python3 evals/subsystem/reporter.py multi \\
      --evals outputs/eval-*.json \\
      --out reports/eval_trend_$(date +%Y%m%d).md

  # Update the canonical glm52_distillation_eval_summary report in place:
  python3 evals/subsystem/reporter.py update-summary \\
      --eval outputs/eval-35b-glm52-distill-iter2-pass1-12task.json \\
      --run-label "35B GLM5.2 iter-2 (ASI3)" \\
      --summary-file reports/glm52_distillation_eval_summary_2026-07-06.md
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_v2(data: dict[str, Any]) -> bool:
    return data.get("schema_version", 1) >= 2


def get_records(data: dict[str, Any], model_key: str) -> list[dict[str, Any]]:
    if _is_v2(data):
        return data.get("results", {}).get(model_key, {}).get("records", [])
    return [r for r in data.get("records", []) if r.get("model") == model_key]


def task_passed(rec: dict[str, Any]) -> bool:
    if "pass_at_1" in rec:
        return float(rec["pass_at_1"]) > 0
    if "n_pass" in rec:
        return int(rec["n_pass"]) > 0
    return bool(rec.get("passed", False))


def get_summary(data: dict[str, Any], model_key: str) -> dict[str, Any]:
    if _is_v2(data):
        return data.get("results", {}).get(model_key, {}).get("summary", {})
    recs = [r for r in data.get("records", []) if r.get("model") == model_key]
    n = len(recs)
    n_pass = sum(1 for r in recs if task_passed(r))
    return {"pass_at_1": round(n_pass / n, 4) if n else 0.0, "n_tasks": n, "n_pass": n_pass}


def _pct(rate: float) -> str:
    return f"{100 * rate:.1f}%"


def _pass_str(n_pass: int, n_total: int) -> str:
    pct = 100.0 * n_pass / n_total if n_total else 0.0
    return f"{n_pass}/{n_total} ({pct:.1f}%)"


# ─────────────────────────────────────────────────────────────────────────────
# Single-run Markdown report
# ─────────────────────────────────────────────────────────────────────────────

def render_single_report(data: dict[str, Any], label: str | None = None) -> str:
    lines: list[str] = []
    created_at = data.get("created_at_utc", "?")
    base_model = Path(data.get("base_model", "?")).name
    adapter    = data.get("adapter") or "None"
    adapter_name = Path(adapter).parent.name if adapter and adapter != "None" else "None"
    k          = data.get("k", 1)

    run_label = label or f"{base_model} / {adapter_name}"
    lines.append(f"# Eval Report: {run_label}")
    lines.append(f"\n**Created:** {created_at}  ")
    lines.append(f"**Base model:** `{data.get('base_model', '?')}`  ")
    lines.append(f"**Adapter:** `{adapter}`  ")
    lines.append(f"**k (samples/task):** {k}  ")
    lines.append(f"**Tasks:** {len(data.get('task_ids', []))}")

    # Summary table
    lines.append("\n## Summary\n")
    lines.append("| Model | Pass@1 | Rate |")
    lines.append("|:------|:-------|:-----|")

    base_sum    = get_summary(data, "base")
    adapter_sum = get_summary(data, "adapter")

    if base_sum.get("n_tasks"):
        lines.append(
            f"| Base | {base_sum['n_pass']}/{base_sum['n_tasks']} | "
            f"{_pct(base_sum['pass_at_1'])} |"
        )
    if adapter_sum.get("n_tasks"):
        lines.append(
            f"| Adapter | {adapter_sum['n_pass']}/{adapter_sum['n_tasks']} | "
            f"{_pct(adapter_sum['pass_at_1'])} |"
        )
    if base_sum.get("n_tasks") and adapter_sum.get("n_tasks"):
        delta = adapter_sum["pass_at_1"] - base_sum["pass_at_1"]
        lines.append(
            f"| **Delta** | — | **{delta:+.1%}** |"
        )

    # Delta breakdown
    delta = data.get("delta")
    if delta:
        if delta.get("fixed_tasks"):
            lines.append(f"\n**Fixed by adapter:** {', '.join(f'`{t}`' for t in delta['fixed_tasks'])}")
        if delta.get("broken_tasks"):
            lines.append(f"\n**⚠️ Broken by adapter:** {', '.join(f'`{t}`' for t in delta['broken_tasks'])}")

    # Per-task table
    lines.append("\n## Per-task Results\n")
    lines.append("| Task | Domain | Category | Base | Adapter | Change |")
    lines.append("|:-----|:-------|:---------|:-----|:--------|:-------|")

    base_recs = {r["task_id"]: r for r in get_records(data, "base")}
    adp_recs  = {r["task_id"]: r for r in get_records(data, "adapter")}
    all_tasks = sorted(set(base_recs) | set(adp_recs))

    for tid in all_tasks:
        br = base_recs.get(tid)
        ar = adp_recs.get(tid)
        bp = task_passed(br) if br else None
        ap = task_passed(ar) if ar else None
        rec = br or ar or {}
        dom  = rec.get("domain", "?")[:12]
        cat  = rec.get("category", "?")[:20]
        bsym = ("✅" if bp else "❌") if bp is not None else "—"
        asym = ("✅" if ap else "❌") if ap is not None else "—"
        if bp is None or ap is None:
            chg = "—"
        elif ap and not bp:
            chg = "🔧 FIXED"
        elif not ap and bp:
            chg = "💥 BROKEN"
        else:
            chg = "—"
        lines.append(f"| `{tid}` | {dom} | {cat} | {bsym} | {asym} | {chg} |")

    # Failure analysis
    failing_adapter = [
        r for r in get_records(data, "adapter")
        if not task_passed(r)
    ]
    if failing_adapter:
        lines.append("\n## Failure Analysis (Adapter)\n")
        for rec in failing_adapter:
            tid = rec["task_id"]
            fc  = rec.get("failure_category") or (
                rec.get("samples", [{}])[0].get("failure_category") if rec.get("samples") else None
            )
            details = rec.get("details", []) or (
                rec.get("samples", [{}])[0].get("details", []) if rec.get("samples") else []
            )
            lines.append(f"### `{tid}`")
            lines.append(f"- **domain:** {rec.get('domain', '?')}")
            lines.append(f"- **category:** {rec.get('category', '?')}")
            if fc:
                lines.append(f"- **failure_category:** `{fc}`")
            if details:
                lines.append("- **failure details:**")
                for d in details[:5]:
                    lines.append(f"  ```\n  {d[:200]}\n  ```")

    # CE-loss if available
    for model_key in ("base", "adapter"):
        heldout = (
            data.get("results", {}).get(model_key, {}).get("heldout_loss")
            if _is_v2(data) else None
        )
        if heldout and heldout.get("loss") is not None:
            lines.append(f"\n## Held-out CE Loss ({model_key})\n")
            lines.append(f"- **loss:** {heldout['loss']}")
            lines.append(f"- **perplexity:** {heldout['perplexity']}")
            lines.append(f"- **n_examples:** {heldout['n_examples']}")
            lines.append(f"- **n_tokens:** {heldout['n_tokens']}")

    lines.append(f"\n---\n*Generated by `evals/subsystem/reporter.py` at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}*")
    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Multi-run Markdown trend table
# ─────────────────────────────────────────────────────────────────────────────

def render_multi_report(runs: list[tuple[str, dict[str, Any]]], model_key: str = "adapter") -> str:
    lines: list[str] = []
    lines.append("# Multi-Run Trend Report\n")
    lines.append(f"**Model tracked:** {model_key}  ")
    lines.append(f"**Generated:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}  ")
    lines.append(f"**Runs:** {len(runs)}\n")

    # Collect all tasks
    all_tasks: list[str] = []
    seen: set[str] = set()
    for _, data in runs:
        for r in get_records(data, model_key):
            tid = r["task_id"]
            if tid not in seen:
                all_tasks.append(tid)
                seen.add(tid)
    all_tasks.sort()

    # Summary row
    lines.append("## Pass@1 Summary\n")
    lines.append("| Run | Pass@1 | Rate |")
    lines.append("|:----|:-------|:-----|")
    for label, data in runs:
        s = get_summary(data, model_key)
        lines.append(f"| {label} | {s.get('n_pass', '?')}/{s.get('n_tasks', '?')} | {_pct(s.get('pass_at_1', 0))} |")

    # Per-task grid
    lines.append("\n## Per-task Grid\n")
    hdrs = ["| Task |"] + [f" {label[:20]} |" for label, _ in runs]
    lines.append("".join(hdrs))
    divs = ["|:-----|"] + [":-----:|" for _ in runs]
    lines.append("|".join(divs))

    for tid in all_tasks:
        row = [f"| `{tid}` |"]
        for _, data in runs:
            recs = {r["task_id"]: r for r in get_records(data, model_key)}
            rec = recs.get(tid)
            if rec is None:
                sym = " — "
            elif task_passed(rec):
                sym = " ✅ "
            else:
                sym = " ❌ "
            row.append(f" {sym} |")
        lines.append("".join(row))

    lines.append(f"\n---\n*Generated by `evals/subsystem/reporter.py`*")
    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# update-summary: append a new section to the canonical summary file
# ─────────────────────────────────────────────────────────────────────────────

def cmd_update_summary(args: argparse.Namespace) -> None:
    data      = _load(args.eval)
    new_block = render_single_report(data, label=args.run_label)
    summary_path = Path(args.summary_file)

    if summary_path.exists():
        existing = summary_path.read_text(encoding="utf-8")
        # append before the last horizontal rule (if any), else append at end
        sep = "\n---\n"
        if sep in existing:
            idx = existing.rfind(sep)
            new_content = existing[:idx] + sep + new_block
        else:
            new_content = existing + "\n\n---\n\n" + new_block
    else:
        new_content = new_block

    summary_path.write_text(new_content, encoding="utf-8")
    print(f"Updated: {summary_path}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI wiring
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Generate Markdown reports from eval JSON outputs")
    sub  = root.add_subparsers(dest="cmd", required=True)

    p_single = sub.add_parser("single", help="Single-run Markdown report")
    p_single.add_argument("--eval",  type=Path, required=True)
    p_single.add_argument("--label", type=str, default=None, help="Human label for this run")
    p_single.add_argument("--out",   type=Path, default=None, help="Output .md file (default: stdout)")

    p_multi = sub.add_parser("multi", help="Multi-run trend table")
    p_multi.add_argument("--evals", nargs="+", type=Path, required=True)
    p_multi.add_argument("--labels", nargs="*", type=str, default=None)
    p_multi.add_argument("--model", default="adapter", choices=["base", "adapter"])
    p_multi.add_argument("--out", type=Path, default=None)

    p_upd = sub.add_parser("update-summary", help="Append a section to the canonical summary file")
    p_upd.add_argument("--eval",         type=Path, required=True)
    p_upd.add_argument("--run-label",    type=str, default=None)
    p_upd.add_argument("--summary-file", type=str, required=True)

    return root


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "single":
        data = _load(args.eval)
        md   = render_single_report(data, label=args.label)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(md, encoding="utf-8")
            print(f"Written: {args.out}")
        else:
            print(md)

    elif args.cmd == "multi":
        labels = args.labels or [p.stem for p in args.evals]
        if len(labels) < len(args.evals):
            labels += [p.stem for p in args.evals[len(labels):]]
        runs = [(labels[i], _load(p)) for i, p in enumerate(args.evals)]
        md   = render_multi_report(runs, model_key=args.model)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(md, encoding="utf-8")
            print(f"Written: {args.out}")
        else:
            print(md)

    elif args.cmd == "update-summary":
        cmd_update_summary(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

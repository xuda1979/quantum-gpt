#!/usr/bin/env python3
"""Offline analysis and comparison tool for eval JSON outputs.

Consumes the JSON files produced by harness.py (schema_version=2) or the
legacy run_asi2_35b_pass1_eval.py (schema_version=1/absent) and produces:

  - Pretty printed per-task comparison tables
  - Regression detection (tasks that went from PASS→FAIL between runs)
  - Multi-run trend analysis across iterations
  - JSON diff output suitable for programmatic consumption

Usage:
  # Compare two eval outputs (base vs adapter within one run):
  python3 evals/subsystem/analyzer.py compare \\
      --eval outputs/eval-35b-glm52-distill-iter1-pass1.json

  # Compare across multiple runs (multi-run trend):
  python3 evals/subsystem/analyzer.py trend \\
      outputs/eval-35b-iter1.json \\
      outputs/eval-35b-iter2.json \\
      outputs/eval-35b-iter3.json

  # Show per-task failure details for a specific model in one run:
  python3 evals/subsystem/analyzer.py failures \\
      --eval outputs/eval-35b-iter2.json --model adapter
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PASS_SYMBOL = "✅"
FAIL_SYMBOL = "❌"
FIXED_SYMBOL = "🔧"
BROKEN_SYMBOL = "💥"
SAME_SYMBOL = "─"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_v2(data: dict[str, Any]) -> bool:
    return data.get("schema_version", 1) >= 2


def _get_results_v2(data: dict[str, Any], model_key: str) -> dict[str, dict[str, Any]]:
    """Return {task_id: record} for a model from schema_version=2 output."""
    results = data.get("results", {}).get(model_key, {})
    records = results.get("records", [])
    return {r["task_id"]: r for r in records}


def _get_results_v1(data: dict[str, Any], model_key: str) -> dict[str, dict[str, Any]]:
    """Return {task_id: record} for schema_version=1 output (legacy format).

    Two legacy shapes are supported:
      A) `records` is a list of records, each carrying `task_id` and `model`.
      B) `results` is a list of records, each carrying `id` (and no `model`
         because the file describes a single model — the v1 scorecard format
         produced by the old `score.py`).
    For shape B the `model_key` argument is ignored.
    """
    records = data.get("records")
    if isinstance(records, list):
        return {r["task_id"]: r for r in records if r.get("model") == model_key}
    # v1 scorecard shape: results is a list of per-task records keyed by `id`
    recs = data.get("results")
    if isinstance(recs, list):
        return {r["id"]: r for r in recs if "id" in r}
    return {}


def get_results(data: dict[str, Any], model_key: str) -> dict[str, dict[str, Any]]:
    if _is_v2(data):
        return _get_results_v2(data, model_key)
    return _get_results_v1(data, model_key)


def task_passed(rec: dict[str, Any]) -> bool:
    # v2: pass_at_1 > 0 or n_pass > 0
    if "pass_at_1" in rec:
        return float(rec["pass_at_1"]) > 0
    if "n_pass" in rec:
        return int(rec["n_pass"]) > 0
    # v1: "passed" key
    return bool(rec.get("passed", False))


def get_summary(data: dict[str, Any], model_key: str) -> dict[str, Any]:
    if _is_v2(data):
        return data.get("results", {}).get(model_key, {}).get("summary", {})
    # v1: rebuild summary from records
    recs = list(get_results(data, model_key).values())
    n = len(recs)
    n_pass = sum(1 for r in recs if task_passed(r))
    return {
        "pass_at_1": round(n_pass / n, 4) if n else 0.0,
        "n_tasks": n,
        "n_pass": n_pass,
    }


def _fmt_pass(n_pass: int, n_total: int) -> str:
    pct = 100.0 * n_pass / n_total if n_total else 0.0
    return f"{n_pass}/{n_total} ({pct:.1f}%)"


# ─────────────────────────────────────────────────────────────────────────────
# compare: base vs adapter in a single eval output
# ─────────────────────────────────────────────────────────────────────────────


def cmd_compare(args: argparse.Namespace) -> None:
    data = _load(args.eval)
    base_recs = get_results(data, "base")
    adapter_recs = get_results(data, "adapter")
    base_sum = get_summary(data, "base")
    adapter_sum = get_summary(data, "adapter")

    all_tasks = sorted(set(base_recs) | set(adapter_recs))

    print(f"\n{'='*70}")
    print(f"Eval comparison: {args.eval.name}")
    print(f"  Base model:    {data.get('base_model', '?')}")
    print(f"  Adapter:       {data.get('adapter', '?')}")
    print(f"  Created at:    {data.get('created_at_utc', '?')}")
    if data.get("k"):
        print(f"  k (samples):   {data['k']}")
    print(f"{'='*70}\n")

    # per-task table
    col_w = max(len(t) for t in all_tasks) + 2
    hdr = f"{'Task':{col_w}} {'Domain':10} {'Category':25} {'Base':6} {'Adapter':8} {'Change':8}"
    print(hdr)
    print("-" * len(hdr))
    for tid in all_tasks:
        br = base_recs.get(tid)
        ar = adapter_recs.get(tid)
        bp = task_passed(br) if br else None
        ap = task_passed(ar) if ar else None
        dom = (br or ar or {}).get("domain", "?")[:10]
        cat = (br or ar or {}).get("category", "?")[:25]
        bsym = (PASS_SYMBOL if bp else FAIL_SYMBOL) if bp is not None else "?"
        asym = (PASS_SYMBOL if ap else FAIL_SYMBOL) if ap is not None else "?"
        if bp is None or ap is None:
            chg = "?"
        elif ap and not bp:
            chg = FIXED_SYMBOL
        elif not ap and bp:
            chg = BROKEN_SYMBOL
        else:
            chg = SAME_SYMBOL
        print(f"{tid:{col_w}} {dom:10} {cat:25} {bsym:6} {asym:8} {chg}")

    print()
    print("Summary:")
    print(f"  Base:    {_fmt_pass(base_sum['n_pass'], base_sum['n_tasks'])} pass@1")
    print(f"  Adapter: {_fmt_pass(adapter_sum['n_pass'], adapter_sum['n_tasks'])} pass@1")
    delta = adapter_sum.get("pass_at_1", 0.0) - base_sum.get("pass_at_1", 0.0)
    print(f"  Delta:   {delta:+.1%}")

    # delta from v2 payload
    if _is_v2(data) and data.get("delta"):
        d = data["delta"]
        if d.get("fixed_tasks"):
            print(f"\n  Fixed by adapter:  {', '.join(d['fixed_tasks'])}")
        if d.get("broken_tasks"):
            print(f"  Broken by adapter: {', '.join(d['broken_tasks'])}")

    # by-domain breakdown
    if _is_v2(data):
        for model_key in ("base", "adapter"):
            s = get_summary(data, model_key)
            by_dom = s.get("by_domain", {})
            if by_dom:
                print(f"\n  {model_key.capitalize()} by domain:")
                for dom, info in sorted(by_dom.items()):
                    print(f"    {dom:12}: {_fmt_pass(info['n_pass'], info['n'])}")


# ─────────────────────────────────────────────────────────────────────────────
# trend: compare adapter pass@1 across multiple eval runs
# ─────────────────────────────────────────────────────────────────────────────


def cmd_trend(args: argparse.Namespace) -> None:
    runs: list[tuple[str, dict[str, Any]]] = []
    for path in args.evals:
        data = _load(path)
        runs.append((path.name, data))

    if not runs:
        print("No eval files provided.")
        return

    # collect all task IDs
    all_tasks: list[str] = []
    seen: set[str] = set()
    for _, data in runs:
        for model_key in ("adapter", "base"):
            for tid in get_results(data, model_key):
                if tid not in seen:
                    all_tasks.append(tid)
                    seen.add(tid)
    all_tasks.sort()

    model_key = args.model  # "adapter" by default

    print(f"\nTrend report — model: {model_key}")
    print(f"{'Task':{max(len(t) for t in all_tasks)+2}}", end="")
    for name, _ in runs:
        print(f"  {name[:20]:20}", end="")
    print()
    print("-" * (max(len(t) for t in all_tasks) + 2 + 22 * len(runs)))

    for tid in all_tasks:
        print(f"{tid:{max(len(t) for t in all_tasks)+2}}", end="")
        for _, data in runs:
            recs = get_results(data, model_key)
            rec = recs.get(tid)
            if rec is None:
                sym = " ? "
            elif task_passed(rec):
                sym = " ✅ "
            else:
                sym = " ❌ "
            print(f"  {sym:20}", end="")
        print()

    print("\nPass@1 summary:")
    for name, data in runs:
        s = get_summary(data, model_key)
        print(f"  {name[:40]:40} → {_fmt_pass(s['n_pass'], s['n_tasks'])}")


# ─────────────────────────────────────────────────────────────────────────────
# failures: show failure details for a model
# ─────────────────────────────────────────────────────────────────────────────


def cmd_failures(args: argparse.Namespace) -> None:
    data = _load(args.eval)
    recs = get_results(data, args.model)

    failing = {tid: rec for tid, rec in recs.items() if not task_passed(rec)}
    if not failing:
        print(f"No failures for model={args.model} in {args.eval.name}")
        return

    print(f"\nFailure report — model={args.model}, eval={args.eval.name}")
    print(f"{len(failing)} failing tasks:\n")

    for tid, rec in sorted(failing.items()):
        print(f"{'─'*60}")
        print(f"Task: {tid}")
        print(f"  domain:   {rec.get('domain', '?')}")
        print(f"  category: {rec.get('category', '?')}")
        fc = rec.get("failure_category") or (
            rec.get("samples", [{}])[0].get("failure_category") if rec.get("samples") else None
        )
        if fc:
            print(f"  failure_category: {fc}")
        # details from v1 flat records
        details = rec.get("details", [])
        if not details and rec.get("samples"):
            details = rec["samples"][0].get("details", [])
        if details:
            print("  details (first 5):")
            for d in details[:5]:
                print(f"    {d[:120]}")
        # code head
        code_head = rec.get("code_head") or (
            rec.get("samples", [{}])[0].get("code_head") if rec.get("samples") else None
        )
        if code_head:
            print(f"  generated code (first 200 chars):\n    {code_head[:200]!r}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# json-diff: machine-readable diff between base and adapter
# ─────────────────────────────────────────────────────────────────────────────


def cmd_json_diff(args: argparse.Namespace) -> None:
    data = _load(args.eval)
    base_recs = get_results(data, "base")
    adapter_recs = get_results(data, "adapter")
    all_tasks = sorted(set(base_recs) | set(adapter_recs))

    out: list[dict[str, Any]] = []
    for tid in all_tasks:
        br = base_recs.get(tid)
        ar = adapter_recs.get(tid)
        bp = task_passed(br) if br else None
        ap = task_passed(ar) if ar else None
        if bp is None and ap is None:
            continue
        change: str
        if ap is True and bp is False:
            change = "fixed"
        elif ap is False and bp is True:
            change = "broken"
        elif ap is True and bp is True:
            change = "both_pass"
        else:
            change = "both_fail"
        out.append(
            {
                "task_id": tid,
                "domain": (br or ar or {}).get("domain"),
                "category": (br or ar or {}).get("category"),
                "base_pass": bp,
                "adapter_pass": ap,
                "change": change,
            }
        )

    print(json.dumps(out, indent=2, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────────────────────
# CLI wiring
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Offline analysis of quantum-gpt eval outputs")
    sub = root.add_subparsers(dest="cmd", required=True)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare base vs adapter in one eval file")
    p_cmp.add_argument("--eval", type=Path, required=True)

    # trend
    p_trend = sub.add_parser("trend", help="Compare adapter pass@1 across multiple eval runs")
    p_trend.add_argument("evals", nargs="+", type=Path)
    p_trend.add_argument("--model", default="adapter", choices=["base", "adapter"])

    # failures
    p_fail = sub.add_parser("failures", help="Show failure details for a model in one eval file")
    p_fail.add_argument("--eval", type=Path, required=True)
    p_fail.add_argument("--model", default="adapter", choices=["base", "adapter"])

    # json-diff
    p_diff = sub.add_parser("json-diff", help="Machine-readable task-level diff (stdout JSON)")
    p_diff.add_argument("--eval", type=Path, required=True)

    return root


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "compare": cmd_compare,
        "trend": cmd_trend,
        "failures": cmd_failures,
        "json-diff": cmd_json_diff,
    }
    dispatch[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

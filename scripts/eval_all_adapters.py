#!/usr/bin/env python3
"""
Comprehensive multi-adapter evaluation coordinator.

Waits for training PIDs to finish (or runs immediately if NOWAIT=1),
then evaluates BASE vs every listed adapter sequentially.
Writes per-adapter JSON results + unified summary to NAS.

Usage (run inside Huanxin NPU environment):
  python3 scripts/eval_all_adapters.py \
      --base /path/to/base_model \
      --adapters /path/a/adapter /path/b/adapter ... \
      --eval-file /path/eval.jsonl \
      --out-dir /path/to/output_dir \
      --wait-pid 12345 \
      --limit 50 \
      --device npu:0

Environment:
  NOWAIT=1    Skip PID wait (eval immediately)
  LIMIT=N     Override --limit
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg: str):
    print(f"[{now_utc()}] {msg}", flush=True)

def wait_for_pid(pid: int, poll_secs: int = 30):
    log(f"Waiting for training PID {pid} to finish...")
    while True:
        r = subprocess.run(["ps", "-p", str(pid)], capture_output=True)
        if r.returncode != 0:
            log(f"PID {pid} has exited.")
            return
        time.sleep(poll_secs)

def run_eval(base: str, adapter: str, eval_file: str, out_path: str,
             device: str, max_new_tokens: int, limit: int) -> dict:
    """Run eval_base_vs_adapter.py for one adapter and return parsed results."""
    script = Path(__file__).parent / "eval_base_vs_adapter.py"
    cmd = [
        "python3", str(script),
        "--base", base,
        "--adapter", adapter,
        "--eval-file", eval_file,
        "--out", out_path,
        "--device", device,
        "--max-new-tokens", str(max_new_tokens),
        "--limit", str(limit),
    ]
    log(f"  Running: {' '.join(cmd)}")
    start = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    log(f"  Finished in {elapsed/60:.1f} min, exit={r.returncode}")
    if r.returncode != 0:
        log(f"  STDERR: {r.stderr[-500:]}")
        return {"error": r.stderr[-300:], "exit_code": r.returncode}
    try:
        return json.load(open(out_path))
    except Exception as e:
        return {"error": str(e), "raw_stderr": r.stderr[-200:]}

def _extract_pass1(res: dict, key: str) -> float | None:
    """Extract pass@1 from either flat (base_pass1) or nested (base.pass_at_1) format."""
    # flat keys used by some wrappers
    flat_keys = [f"{key}_pass1", f"{key}_pass_at_1", f"{key}Pass1"]
    for k in flat_keys:
        v = res.get(k)
        if v is not None:
            return float(v)
    # nested format written by eval_base_vs_adapter.py:
    #   {"base": {"pass_at_1": X, ...}, "adapter": {"pass_at_1": Y, ...}}
    nested = res.get(key)
    if isinstance(nested, dict):
        for nk in ("pass_at_1", "pass1", "pass_at1"):
            v = nested.get(nk)
            if v is not None:
                return float(v)
    return None

def _extract_n_eval(res: dict) -> int | None:
    for k in ("n_eval", "total_evaluated", "total"):
        v = res.get(k)
        if v is not None:
            return int(v)
    # nested
    for key in ("base", "adapter"):
        nested = res.get(key)
        if isinstance(nested, dict):
            v = nested.get("total")
            if v is not None:
                return int(v)
    return None

def _extract_per_fw(res: dict) -> dict:
    """Get per-framework breakdown — prefer adapter's numbers."""
    # nested eval_base_vs_adapter.py format: res["adapter"]["per_framework"]
    for key in ("adapter", "base"):
        nested = res.get(key)
        if isinstance(nested, dict):
            pf = nested.get("per_framework") or nested.get("by_framework")
            if pf:
                return pf
    return res.get("by_framework", {})

def summarise(results: list[dict]) -> dict:
    """Aggregate per-adapter dicts into a comparison table.

    Compatible with both eval_base_vs_adapter.py nested output:
      {"base": {"pass_at_1": X, "total": N, "per_framework": {...}}, "adapter": {...}}
    and flat wrappers that write top-level base_pass1 / adapter_pass1.
    """
    rows = []
    base_pass = None
    for res in results:
        adapter_label = res.get("adapter_label", "?")
        if "error" in res and "base" not in res:
            rows.append({"adapter": adapter_label, "error": res["error"]})
            continue
        bp = _extract_pass1(res, "base")
        ap = _extract_pass1(res, "adapter")
        if base_pass is None and bp is not None:
            base_pass = bp
        delta_top = res.get("delta_pass_at_1")
        delta = float(delta_top) if delta_top is not None else (
            round(ap - bp, 4) if ap is not None and bp is not None else None
        )
        rows.append({
            "adapter": adapter_label,
            "base_pass1": bp,
            "adapter_pass1": ap,
            "delta": delta,
            "n_eval": _extract_n_eval(res),
            "by_framework": _extract_per_fw(res),
        })
    return {
        "generated_at": now_utc(),
        "base_pass1": base_pass,
        "adapters": rows,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--eval-file", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--wait-pid", type=int, default=0)
    ap.add_argument("--device", default="npu:0")
    ap.add_argument("--max-new-tokens", type=int, default=768)
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()

    limit = int(os.environ.get("LIMIT", args.limit))
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    # Wait for training if PID given
    if args.wait_pid and not os.environ.get("NOWAIT"):
        wait_for_pid(args.wait_pid)
        time.sleep(10)  # allow final checkpoints to flush

    log(f"Starting comprehensive eval: {len(args.adapters)} adapters, limit={limit}")
    log(f"  Base: {args.base}")
    log(f"  Eval: {args.eval_file}")

    per_adapter_results = []
    for i, adapter in enumerate(args.adapters):
        adapter_label = Path(adapter).parts[-2] if Path(adapter).name == "adapter" else Path(adapter).name
        out_path = str(Path(args.out_dir) / f"eval_{adapter_label}.json")
        log(f"\n[{i+1}/{len(args.adapters)}] Evaluating adapter: {adapter_label}")
        res = run_eval(
            base=args.base, adapter=adapter, eval_file=args.eval_file,
            out_path=out_path, device=args.device,
            max_new_tokens=args.max_new_tokens, limit=limit
        )
        res["adapter_label"] = adapter_label
        per_adapter_results.append(res)

    # Write unified summary
    summary = summarise(per_adapter_results)
    summary_path = str(Path(args.out_dir) / "eval_summary.json")
    json.dump(summary, open(summary_path, "w"), indent=2)
    log(f"\n{'='*60}")
    log(f"EVAL COMPLETE — summary: {summary_path}")
    log(f"Base pass@1: {summary['base_pass1']}")
    for row in summary["adapters"]:
        if "error" in row:
            log(f"  {row['adapter'][:60]}: ERROR")
        else:
            log(f"  {Path(row['adapter']).parts[-2] if row['adapter'].endswith('/adapter') else row['adapter'][:40]}: "
                f"adapter={row['adapter_pass1']} delta={row['delta']:+.3f}" if row.get('delta') is not None
                else f"  {row.get('adapter','?')}: no result")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""reeval_report.py — comprehensive base-vs-adapter re-eval report (many rows).

Reads the re-extracted emissions (eval100_{base,adapter}_re.jsonl) plus the
judge shards (reeval_judge_shard*.jsonl) when available and prints a full
comparison table: emission metrics, extraction metrics, exec metrics, judge
dimensions, and the comprehensive blend.

Usage: reeval_report.py [--out report.md]
"""

import glob
import json

OUT = "/root/work/quantum-gpt/outputs"
P_MASS, S_MASS, J_MASS = 0.40, 0.35, 0.25


def load_emissions(which):
    rows = []
    for f in glob.glob(f"{OUT}/eval100_{which}_re.jsonl"):
        rows.extend(json.loads(line) for line in open(f, encoding="utf-8"))
    by_idx = {r["sample_idx"]: r for r in rows}
    return by_idx


def load_judge():
    rows = []
    for f in glob.glob(f"{OUT}/reeval_judge_shard*.jsonl"):
        rows.extend(json.loads(line) for line in open(f, encoding="utf-8"))
    return {r["sample_idx"]: r for r in rows}


def fmt(v, nd=3):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def main():
    base = load_emissions("base")
    adapter = load_emissions("adapter")
    judge = load_judge()
    rows = []

    def row(name, fn, pct=False, nd=3):
        b = fn(base)
        a = fn(adapter)
        d = None if (b is None or a is None) else a - b
        rows.append((name, b, a, d, pct, nd))

    # ---- emission / extraction metrics -----------------------------------
    def mean_resp(r):
        vals = [len(v.get("response") or "") for v in r.values()]
        return (sum(vals) / len(vals)) if vals else None

    def frac_code(r):
        vals = [1 if (v.get("extract_method") or "") != "none" else 0 for v in r.values()]
        return (sum(vals) / len(vals)) if vals else None

    def frac_method(m):
        return lambda r: (
            (sum(1 for v in r.values() if m in (v.get("extract_method") or "")) / len(r))
            if r
            else None
        )

    row("n_samples", lambda r: float(len(r)) if r else None, nd=0)
    row("mean_response_len", mean_resp, nd=0)
    row("pct_answers_with_code", frac_code, pct=True)
    row("pct_fenced_python", frac_method("fence[python]"), pct=True)
    row("pct_fenced_broken", frac_method("[unparsed]"), pct=True)
    row("pct_fenced_qsharp", frac_method("fence[qsharp]"), pct=True)
    row("pct_span_extracted", frac_method("span"), pct=True)
    row("pct_no_code", frac_method("none"), pct=True)

    # ---- exec metrics -----------------------------------------------------
    def exec_frac(reason=None, passed=None):
        def f(r):
            vals = [
                1
                if (passed is None or bool(v["exec"].get("passed")) == passed)
                and (reason is None or v["exec"].get("reason", "rc_fail") == reason)
                else 0
                for v in r.values()
            ]
            return (sum(vals) / len(vals)) if vals else None

        return f

    def mean_runtime(r):
        vals = [
            v["exec"].get("runtime_ms")
            for v in r.values()
            if isinstance(v["exec"].get("runtime_ms"), int | float)
        ]
        return (sum(vals) / len(vals)) if vals else None

    row("exec_pass_rate", exec_frac(passed=True), pct=True)
    row("syntax_error_rate", exec_frac(passed=False, reason="syntax_error"), pct=True)
    row("empty_code_rate", exec_frac(passed=False, reason="empty_code"), pct=True)
    row("trivial_code_rate", exec_frac(passed=False, reason="trivial_code"), pct=True)
    row("rc_fail_rate", exec_frac(passed=False, reason="rc_fail"), pct=True)
    row("mean_runtime_ms", mean_runtime, nd=0)

    # ---- judge metrics (after judge phase) --------------------------------
    if judge:

        def jrec(r, i):
            return (judge.get(i, {}) or {}).get("base" if r is base else "adapter")

        for dim in ("correctness", "runnability", "result_correctness", "efficiency", "quality"):

            def judge_dim(r, dim=dim):
                vals = [
                    rec["judge_dims"][dim]
                    for i in sorted(r)
                    if (rec := jrec(r, i))
                    and rec.get("judge_dims") is not None
                    and rec["judge_dims"].get(dim) is not None
                ]
                return (sum(vals) / len(vals)) if vals else None

            row(f"judge_{dim}", judge_dim)

        def judge_mean_J(r):
            vals = []
            for i in sorted(r):
                rec = jrec(r, i)
                if not rec or not rec.get("judge_dims"):
                    continue
                dims = [v for v in rec["judge_dims"].values() if v is not None]
                if dims:
                    vals.append(sum(dims) / len(dims))
            return (sum(vals) / len(vals)) if vals else None

        row("judge_mean_J", judge_mean_J)

        def comp_mean(r):
            vals = [
                rec["comprehensive"]
                for i in sorted(r)
                if (rec := jrec(r, i)) and rec.get("comprehensive") is not None
            ]
            return (sum(vals) / len(vals)) if vals else None

        row("comprehensive_R", comp_mean)

        def result_match_rate(r):
            vals = [
                1 if rec.get("result_match") is True else 0
                for i in sorted(r)
                if (rec := jrec(r, i)) and rec.get("result_match") is not None
            ]
            return (sum(vals) / len(vals)) if vals else None

        row("result_match_rate", result_match_rate, pct=True)

    # ---- print table -------------------------------------------------------
    out = []
    out.append("| metric | base | adapter | delta |")
    out.append("|--------|------|---------|-------|")
    for name, b, a, _d, pct, nd in rows:
        if b is None and a is None:
            continue
        fmtv = (
            (lambda v: (f"{v*100:.1f}%" if v is not None else "n/a"))
            if pct
            else (lambda v, nd=nd: fmt(v, nd))
        )
        dv = (a - b) if (b is not None and a is not None) else None
        dstr = (
            (f"{dv*100:+.1f}pp" if pct and dv is not None else fmt(dv, nd))
            if dv is not None
            else "n/a"
        )
        out.append(f"| {name} | {fmtv(b)} | {fmtv(a)} | {dstr} |")
    print("\n".join(out))
    jn = len(judge)
    print(f"\njudge records: {jn}/100 (base+adapter per sample)")


if __name__ == "__main__":
    main()

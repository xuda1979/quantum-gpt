#!/usr/bin/env python3
"""Domain regression gate - BLOCK a training launch if any domain regressed.

Industrial-standard continuous gate for the domain-performance monitor
(evals/domain_monitor/README.md): before a new warm-continue launch, compare
the candidate adapter per-domain composite (math / coding / physics / qis)
against the PREVIOUS checkpoint. If ANY domain drops by more than
--max-composite-drop (default 0.10) the gate exits NONZERO and the launch is
blocked; only an all-green gate lets a warm-continue proceed.

Inputs (first match wins):
  1. --drift-report PATH
       domain_drift_report.py JSON: domains.<d>.composite_base /
       composite_adapter (aliases: base/adapter; or top-level baseline /
       candidate domain->composite maps).
  2. --baseline-dir DIR + --candidate-dir DIR
       Raw results dirs (results/<adapter>/) holding <domain>_<date>.json
       files; the NEWEST dated file per domain is the measurement.
  3. --results-root ROOT  (default evals/domain_monitor/results)
       Launch-guard mode. With --baseline-adapter/--candidate-adapter named
       dirs are used; otherwise AUTO: the two newest adapter dirs under the
       root - second-newest = baseline (previous checkpoint), newest =
       candidate (pending warm-continue).

Composite bar (same as scripts/verdict_holdout.py):
    composite = 0.70 * rubric_overall + 0.30 * pass@1
A precomputed "composite" field is trusted when present; otherwise it is
recomputed from "records"; scalar aliases (avg_rubric / mean_overall) are the
last resort.

Fail-closed: a missing/unreadable/unmeasurable required domain on either side
is RED, never a silent pass; zero measurable domains is RED.

Exit codes: 0 = GREEN (warm-continue may proceed), 1 = RED (regression or
unmeasurable domain), 2 = input error (no source / unreadable inputs).

Training launch-guard integration (one line before any warm-continue launch):
  python3 scripts/domain_regression_gate.py --results-root evals/domain_monitor/results || exit 1
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

RUBRIC_WEIGHT = 0.70
PASS_WEIGHT = 0.30
DEFAULT_MAX_COMPOSITE_DROP = 0.10
DEFAULT_RESULTS_ROOT = Path("evals/domain_monitor/results")
DEFAULT_REQUIRED_DOMAINS = ("math", "coding", "physics", "qis")
KIND = "domain_regression_gate"
_EPS = 1e-9

_BASE_KEYS = ("composite_base", "base_composite", "baseline_composite", "base", "baseline")
_CAND_KEYS = (
    "composite_adapter",
    "adapter_composite",
    "candidate_composite",
    "adapter",
    "candidate",
)
_COMPOSITE_KEYS = ("composite", "avg_composite", "mean_composite", "score_composite")
_RUBRIC_KEYS = ("avg_rubric", "mean_rubric", "mean_overall", "avg_overall", "rubric", "overall")
_FILENAME_DATE_RE = re.compile(r"^(?P<domain>.+?)_(?P<date>\d{8})")


class GateInputError(Exception):
    """Unusable gate inputs - fail-closed, exit 2 (still blocks the launch)."""


def _finite(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def candidate_composite(entry):
    """Composite for one domain result entry (float or None if unmeasurable).

    Trusts a precomputed composite; else recomputes 0.70*rubric + 0.30*pass@1
    from records (the verdict_holdout bar); else scalar rubric aliases.
    """
    if not isinstance(entry, dict):
        return None
    for key in _COMPOSITE_KEYS:
        value = entry.get(key)
        if _finite(value):
            return float(value)
    records = entry.get("records")
    if isinstance(records, list) and records:
        rubric_vals = []
        passes = 0
        for rec in records:
            if not isinstance(rec, dict):
                continue
            scores = rec.get("scores")
            overall = scores.get("overall") if isinstance(scores, dict) else None
            rubric_vals.append(float(overall) if _finite(overall) else 0.0)
            if rec.get("passed"):
                passes += 1
        if rubric_vals:
            n = len(rubric_vals)
            return RUBRIC_WEIGHT * (sum(rubric_vals) / n) + PASS_WEIGHT * (passes / n)
    for key in _RUBRIC_KEYS:
        value = entry.get(key)
        if _finite(value):
            return float(value)
    return None


def _pair_from_entry(entry):
    """(base, candidate) composites from one domains.<d> report entry."""
    if not isinstance(entry, dict):
        return (None, None)
    base = None
    cand = None
    for key in _BASE_KEYS:
        value = entry.get(key)
        if isinstance(value, dict):
            base = candidate_composite(value)
        elif _finite(value):
            base = float(value)
        if base is not None:
            break
    for key in _CAND_KEYS:
        value = entry.get(key)
        if isinstance(value, dict):
            cand = candidate_composite(value)
        elif _finite(value):
            cand = float(value)
        if cand is not None:
            break
    return (base, cand)


def load_drift_report(path: Path):
    """Parse a domain_drift_report JSON into (scores, base_label, cand_label)."""
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GateInputError(f"unreadable drift report {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GateInputError(f"drift report {path} is not a JSON object")

    base_label = "baseline"
    cand_label = "candidate"
    baseline = payload.get("baseline")
    cand = payload.get("candidate")
    if isinstance(baseline, dict) and baseline.get("label"):
        base_label = str(baseline["label"])
    if isinstance(cand, dict) and cand.get("label"):
        cand_label = str(cand["label"])

    scores = dict()
    domains_block = payload.get("domains")
    if isinstance(domains_block, dict) and domains_block:
        for domain, entry in domains_block.items():
            scores[str(domain)] = _pair_from_entry(entry)
        return (scores, base_label, cand_label)

    # Mapping form: baseline/candidate are domain -> composite maps.
    if isinstance(baseline, dict) and isinstance(cand, dict):
        for domain, value in baseline.items():
            if domain == "label":
                continue
            if _finite(value):
                scores.setdefault(str(domain), (None, None))
                scores[str(domain)] = (float(value), scores[str(domain)][1])
        for domain, value in cand.items():
            if domain == "label":
                continue
            if _finite(value):
                scores.setdefault(str(domain), (None, None))
                scores[str(domain)] = (scores[str(domain)][0], float(value))
        if scores:
            return (scores, base_label, cand_label)

    raise GateInputError(f"no per-domain composites found in drift report {path}")


def _file_sort_key(path: Path):
    match = _FILENAME_DATE_RE.match(path.name)
    date = int(match.group("date")) if match else 0
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        mtime = 0
    return (date, mtime)


def newest_entries(results_dir: Path):
    """domain -> newest result entry from <domain>_<date>.json files."""
    results_dir = Path(results_dir)
    try:
        files = sorted(results_dir.glob("*.json"), key=_file_sort_key)
    except OSError as exc:
        raise GateInputError(f"unreadable results dir {results_dir}: {exc}") from exc
    entries = dict()
    for path in files:
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # a torn/partial file never wins; newer readable files do
        match = _FILENAME_DATE_RE.match(path.name)
        if match:
            domain = str(match.group("domain"))
        elif isinstance(entry, dict) and entry.get("domain"):
            domain = str(entry["domain"])
        else:
            domain = path.stem
        entries[domain] = entry
    return entries


def load_results_dir(results_dir: Path):
    """(scores, label) from one adapter results dir (newest file per domain).

    Accepts either the adapter dir itself (holding <domain>_<date>.json) or a
    parent dir containing exactly one adapter subdir (e.g. results/<adapter>/).
    """
    results_dir = Path(results_dir)
    if not results_dir.is_dir():
        raise GateInputError(f"results dir not found: {results_dir}")
    entries = newest_entries(results_dir)
    label = results_dir.name
    if not entries:
        subdirs = [p for p in results_dir.iterdir() if p.is_dir()]
        if len(subdirs) == 1:
            return load_results_dir(subdirs[0])
        raise GateInputError(f"no readable result files in {results_dir}")
    scores = dict()
    for domain, entry in entries.items():
        scores[domain] = (candidate_composite(entry), None)
    return (scores, label)


def _merge_scores(base_scores, cand_scores):
    merged = dict((d, (pair[0], None)) for d, pair in base_scores.items())
    for domain, pair in cand_scores.items():
        prev = merged.get(domain, (None, None))
        merged[domain] = (prev[0], pair[0])
    return merged


def _dir_newest_key(path: Path):
    files = list(path.glob("*.json"))
    if not files:
        return (0, 0)
    return _file_sort_key(max(files, key=_file_sort_key))


def adapter_dirs(results_root: Path):
    """Adapter dirs under a results root, NEWEST first."""
    results_root = Path(results_root)
    if not results_root.is_dir():
        raise GateInputError(f"results root not found: {results_root}")
    dirs = [p for p in results_root.iterdir() if p.is_dir()]
    if not dirs:
        raise GateInputError(f"no adapter dirs under results root {results_root}")
    return sorted(dirs, key=_dir_newest_key, reverse=True)


def resolve_inputs(args):
    """Domain scores + labels from the first available CLI input source."""
    if args.drift_report is not None:
        scores, base_label, cand_label = load_drift_report(args.drift_report)
    elif args.baseline_dir is not None and args.candidate_dir is not None:
        base_scores, base_label = load_results_dir(args.baseline_dir)
        cand_scores, cand_label = load_results_dir(args.candidate_dir)
        scores = _merge_scores(base_scores, cand_scores)
    elif args.results_root is not None:
        if args.baseline_adapter and args.candidate_adapter:
            base_dir = Path(args.results_root) / args.baseline_adapter
            cand_dir = Path(args.results_root) / args.candidate_adapter
            if not base_dir.is_dir():
                raise GateInputError(f"baseline adapter dir not found: {base_dir}")
            if not cand_dir.is_dir():
                raise GateInputError(f"candidate adapter dir not found: {cand_dir}")
        else:
            dirs = adapter_dirs(args.results_root)
            if len(dirs) < 2:
                raise GateInputError(
                    f"auto mode needs >=2 adapter dirs under {args.results_root} "
                    f"(found {len(dirs)})"
                )
            cand_dir, base_dir = dirs[0], dirs[1]
        base_scores, base_label = load_results_dir(base_dir)
        cand_scores, cand_label = load_results_dir(cand_dir)
        scores = _merge_scores(base_scores, cand_scores)
    else:
        raise GateInputError(
            "no input source: pass --drift-report, --baseline-dir + --candidate-dir, "
            "or --results-root"
        )
    if args.baseline_adapter:
        base_label = args.baseline_adapter
    if args.candidate_adapter:
        cand_label = args.candidate_adapter

    for domain in args.required_domains:
        if domain not in scores:
            scores[domain] = (None, None)
    return (scores, base_label, cand_label)


def evaluate_gate(domain_scores, max_drop: float, base_label="baseline", cand_label="candidate"):
    """Pure gate decision. RED when any domain is regressed or unmeasurable."""
    rows = []
    failed = []
    unmeasurable = []
    for domain in sorted(domain_scores):
        base, cand = domain_scores[domain]
        if base is None or cand is None:
            unmeasurable.append(domain)
            failed.append(domain)
            rows.append(
                dict(domain=domain, base=base, candidate=cand, delta=None, status="unmeasurable")
            )
            continue
        delta = cand - base
        regressed = delta < -float(max_drop) - _EPS
        if regressed:
            failed.append(domain)
        rows.append(
            dict(
                domain=domain,
                base=base,
                candidate=cand,
                delta=delta,
                status="REGRESSED" if regressed else "ok",
            )
        )
    ok = bool(rows) and not failed
    if not rows:
        reason = "no domain measurements found (fail-closed)"
    elif unmeasurable:
        reason = "unmeasurable required domains: " + ", ".join(unmeasurable)
    else:
        reason = "composite drop beyond threshold on: " + ", ".join(failed)
    return dict(
        kind=KIND,
        ok=ok,
        max_composite_drop=float(max_drop),
        baseline_label=str(base_label),
        candidate_label=str(cand_label),
        rows=rows,
        failed_domains=failed,
        unmeasurable_domains=unmeasurable,
        reason=None if ok else reason,
    )


def gate(domain_scores, threshold: float = DEFAULT_MAX_COMPOSITE_DROP):
    """Programmatic convenience: (ok, failed_domains) for launch-guard callers."""
    result = evaluate_gate(domain_scores, threshold)
    return (result["ok"], list(result["failed_domains"]))


def render_summary(result):
    """Exactly 3 stdout lines: header, per-domain deltas, verdict."""
    status = "GREEN" if result["ok"] else "RED"
    threshold = result["max_composite_drop"]
    n_rows = len(result["rows"])
    line1 = (
        f"DOMAIN REGRESSION GATE: {status}"
        f" threshold={threshold:.2f} domains={n_rows}"
        f" baseline={result['baseline_label']} candidate={result['candidate_label']}"
    )
    parts = []
    for row in result["rows"]:
        if row["status"] == "unmeasurable":
            parts.append(f"{row['domain']} UNMEASURABLE")
        else:
            delta = row["delta"]
            parts.append(
                f"{row['domain']} {row['base']:.4f}->{row['candidate']:.4f} d={delta:+.4f}"
            )
    line2 = "  " + " | ".join(parts)
    if result["ok"]:
        line3 = f"GATE: {status} - warm-continue may proceed"
    else:
        line3 = f"GATE: {status} - LAUNCH BLOCKED ({', '.join(result['failed_domains'])})"
    return [line1, line2, line3]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Domain regression gate: BLOCK a warm-continue launch when any "
        "monitored domain composite regressed vs the previous checkpoint."
    )
    parser.add_argument("--drift-report", type=Path, default=None, help="domain drift report JSON")
    parser.add_argument("--baseline-dir", type=Path, default=None, help="baseline results dir")
    parser.add_argument("--candidate-dir", type=Path, default=None, help="candidate results dir")
    parser.add_argument(
        "--results-root",
        type=Path,
        default=None,
        help=f"shared results root (default {str(DEFAULT_RESULTS_ROOT)}))",
    )
    parser.add_argument("--baseline-adapter", default=None, help="baseline adapter dir name")
    parser.add_argument("--candidate-adapter", default=None, help="candidate adapter dir name")
    parser.add_argument(
        "--max-composite-drop",
        type=float,
        default=DEFAULT_MAX_COMPOSITE_DROP,
        help=f"fail when adapter < base - this (default {DEFAULT_MAX_COMPOSITE_DROP})",
    )
    parser.add_argument(
        "--required-domains",
        default=",".join(DEFAULT_REQUIRED_DOMAINS),
        help="comma-separated domains that MUST be measurable (default: "
        + ",".join(DEFAULT_REQUIRED_DOMAINS)
        + ")",
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="write the gate verdict JSON here"
    )
    args = parser.parse_args(argv)
    args.required_domains = tuple(
        d.strip() for d in str(args.required_domains).split(",") if d.strip()
    )
    if args.results_root is None:
        args.results_root = DEFAULT_RESULTS_ROOT
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        scores, base_label, cand_label = resolve_inputs(args)
    except GateInputError as exc:
        print(f"domain_regression_gate: INPUT ERROR (fail-closed): {exc}", file=sys.stderr)
        return 2
    result = evaluate_gate(scores, args.max_composite_drop, base_label, cand_label)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for line in render_summary(result):
        print(line)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

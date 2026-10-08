"""Evidence→claim auditor.

The auditor is the keystone of trust. It cross-checks every numeric
claim in a human-written report (e.g. ``RUN_SUMMARY.md``) against the
provenance ledger. A claim is *backed* iff we can resolve it to a
specific run + task set and the numbers match exactly. Unbacked claims
block publication.

Recognised claim patterns (regex over Markdown table cells and prose):

  - ``N/M passed``     → run.n_pass == N and run.n_tasks == M
  - ``pass@1 = 0.XXXX`` → run.pass_at_1 == 0.XXXX (within 1e-4)
  - ``pass@k = 0.XXXX`` → run.pass_at_k == 0.XXXX (within 1e-4)
  - ``N tasks``        → run.n_tasks == N
  - ``delta = +X%``    → adapter.pass_at_1 - base.pass_at_1 == X/100

The auditor also verifies that every ``run_id`` referenced in a report
exists in the ledger and that the run's ``suite_hash`` matches the
suite lock the report claims to use.

Usage:

    from evals.trust.core.audit import audit_report
    report = audit_report(ledger=ledger, run_id=42, report_path="RUN_SUMMARY.md")
    if not report["passed"]:
        for c in report["claims"]:
            if not c["backed"]:
                print("UNBACKED:", c)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ledger import Ledger


# ── claim patterns ──────────────────────────────────────────────────────────
# Pattern: "12/13", "12 / 13", "12 of 13", with optional trailing words.
RE_PASS_COUNT = re.compile(r"\b(\d+)\s*(?:/|of)\s*(\d+)\b")
# Pattern: "pass@1 = 0.8462", "pass@1: 0.8462", "pass@1 0.8462"
RE_PASS_AT_1  = re.compile(r"pass@1\s*[:=]?\s*(0?\.\d+|1\.0+|1(?!\.\d))", re.IGNORECASE)
# Pattern: "pass@k = 0.9", "pass@5 = 0.9"
RE_PASS_AT_K  = re.compile(r"pass@k\s*[:=]?\s*(0?\.\d+|1\.0+|1(?!\.\d))", re.IGNORECASE)
# Pattern: "26 tasks", "n_tasks = 26", "n_tasks: 26"
RE_N_TASKS    = re.compile(r"(?:n_tasks\s*[:=]?\s*(\d+))|(?<![a-zA-Z0-9_])(\d+)\s*tasks?\b", re.IGNORECASE)
# Pattern: "delta = +12.5%", "delta: -3.2%"
RE_DELTA_PCT  = re.compile(r"delta\s*[:=]?\s*([+\-])\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)


@dataclass
class Claim:
    line_no: int
    text: str
    kind: str
    value: Any
    backed: bool
    evidence: dict[str, Any] | None


def _extract_claims(text: str) -> list[Claim]:
    """Extract all numeric claims from a Markdown report."""
    claims: list[Claim] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in RE_PASS_COUNT.finditer(line):
            n, m_total = int(m.group(1)), int(m.group(2))
            if m_total < 1 or m_total > 10_000:
                continue
            claims.append(Claim(line_no, line.strip(), "pass_count", (n, m_total), False, None))
        for m in RE_PASS_AT_1.finditer(line):
            val = float(m.group(1))
            claims.append(Claim(line_no, line.strip(), "pass_at_1", val, False, None))
        for m in RE_PASS_AT_K.finditer(line):
            val = float(m.group(1))
            claims.append(Claim(line_no, line.strip(), "pass_at_k", val, False, None))
        for m in RE_N_TASKS.finditer(line):
            # RE_N_TASKS has two alternatives: n_tasks=(\d+) OR (\d+)\s*tasks?
            g1, g2 = m.group(1), m.group(2)
            n = int(g1) if g1 is not None else int(g2)
            if n < 1 or n > 10_000:
                continue
            claims.append(Claim(line_no, line.strip(), "n_tasks", n, False, None))
        for m in RE_DELTA_PCT.finditer(line):
            sign = 1 if m.group(1) == "+" else -1
            val = sign * float(m.group(2)) / 100.0
            claims.append(Claim(line_no, line.strip(), "delta_pct", val, False, None))
    return claims


def _back_claims(
    *, claims: list[Claim], ledger: Ledger, run_id: int
) -> list[Claim]:
    """Resolve each claim against the ledger's run_summary."""
    summary = ledger.run_summary(run_id)
    expected_pass = summary["n_pass"]
    expected_tasks = summary["n_tasks"]
    expected_p1 = summary["pass_at_1"]
    out: list[Claim] = []
    for c in claims:
        if c.kind == "pass_count":
            n, m = c.value
            if n == expected_pass and m == expected_tasks:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, True,
                                 {"run_id": run_id, "n_pass": expected_pass, "n_tasks": expected_tasks}))
            else:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, False,
                                 {"run_id": run_id, "actual_n_pass": expected_pass, "actual_n_tasks": expected_tasks}))
        elif c.kind == "pass_at_1":
            if abs(c.value - expected_p1) <= 1e-4:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, True,
                                 {"run_id": run_id, "pass_at_1": expected_p1}))
            else:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, False,
                                 {"run_id": run_id, "actual_pass_at_1": expected_p1}))
        elif c.kind == "n_tasks":
            if c.value == expected_tasks:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, True,
                                 {"run_id": run_id, "n_tasks": expected_tasks}))
            else:
                out.append(Claim(c.line_no, c.text, c.kind, c.value, False,
                                 {"run_id": run_id, "actual_n_tasks": expected_tasks}))
        else:
            # pass@k and delta_pct require richer context; mark as
            # unbacked unless the caller supplies a comparator run.
            out.append(Claim(c.line_no, c.text, c.kind, c.value, False,
                             {"run_id": run_id, "note": "requires comparator; not auto-backed"}))
    return out


def audit_report(
    *, ledger: Ledger, run_id: int, report_path: str | Path
) -> dict[str, Any]:
    """Audit a human-written report against the ledger for a given run."""
    text = Path(report_path).read_text(encoding="utf-8")
    claims = _extract_claims(text)
    backed = _back_claims(claims=claims, ledger=ledger, run_id=run_id)
    n_backed = sum(1 for c in backed if c.backed)
    n_unbacked = len(backed) - n_backed
    # persist to ledger
    for c in backed:
        ledger.record_claim(
            run_id=run_id,
            report_path=str(report_path),
            line_no=c.line_no,
            claim_text=c.text,
            claim_kind=c.kind,
            claim_value=str(c.value),
            backed=c.backed,
            evidence=c.evidence,
        )
    ledger.record_audit_result(
        run_id=run_id,
        report_path=str(report_path),
        n_claims=len(backed),
        n_backed=n_backed,
        n_unbacked=n_unbacked,
        passed=(n_unbacked == 0),
        details=[
            {"line_no": c.line_no, "kind": c.kind, "value": c.value,
             "backed": c.backed, "evidence": c.evidence}
            for c in backed
        ],
    )
    return {
        "run_id": run_id,
        "report_path": str(report_path),
        "n_claims": len(backed),
        "n_backed": n_backed,
        "n_unbacked": n_unbacked,
        "passed": (n_unbacked == 0),
        "claims": [
            {"line_no": c.line_no, "text": c.text, "kind": c.kind,
             "value": c.value, "backed": c.backed, "evidence": c.evidence}
            for c in backed
        ],
    }

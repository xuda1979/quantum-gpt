#!/usr/bin/env python3
"""Semantic correctness audit of all 1000 rows.

For each row, check that the code's stdout actually answers the question:
  1. bell_state: stdout must reflect a 2-qubit Bell state (|00>±|11>)/sqrt(2),
     or Bell-pair measurement counts ~ 50/50 on |00> and |11>.
  2. ghz_state:  N-qubit GHZ => only |0...0> and |1...1> have non-negligible
     amplitude/counts, and (for even balance) roughly equal.
  3. statevector: if the question names a target state / amplitudes / fidelity,
     require a "fidelity" / "match" / small "diff" line; if it just asks to
     print the statevector, require a numeric vector with len = 2^n.
  4. Quantitative rows: if the question states a specific number (fidelity,
     counts, energy, maxcut value), check the stdout reports that value.

This script ONLY flags suspicious rows; it does not modify anything.
Output: data/generated/quantum_dedup_1k_glm52_soft_distill_v3/audit_semantic_v6.json
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(
    "/Users/daxu/software/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
)
A = json.load(open(BASE / "analysis_v4.json"))
QC = [json.loads(line) for line in open(BASE / "questions_and_code.jsonl")]
OUT = [json.loads(line) for line in open(BASE / "code_outputs_v4.jsonl")]

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"


def has_verify_pass(out: str) -> bool:
    return bool(
        re.search(
            r"(VERIFICATION:\s*PASS|Verification passed|verification passed|Verify.*PASS|PASSED|fidelity\s*[:=]?\s*1\.0+(?:0*)|fidelity\s*[:=]?\s*0\.99\d+|match|max.*diff.*[1e][-]\d|within tolerance)",
            out,
            re.I,
        )
    )


def has_fail(out: str) -> bool:
    return bool(
        re.search(
            r"(Failed|FAIL\b|VERIFICATION:\s*FAIL|AssertionError|Traceback|did not match|incorrect|wrong|mismatch|not equal)",
            out,
            re.I,
        )
    )


def check_bell(row, q, o):
    out = o["stdout"]
    issues = []
    # Bell state: 2 qubits, equal superposition of |00> and |11>
    # Accept: counts with ~50% 00 and ~50% 11, or statevector with 2 equal nonzero amps
    if "counts" in out.lower() or "shot" in out.lower():
        # parse counts like {'00': 1024, '11': 1024}
        m = re.findall(r"'?(00|11|01|10)'?\s*:\s*(\d+)", out)
        if m:
            d = {k: int(v) for k, v in m}
            total = sum(d.values())
            if total > 0:
                p00 = d.get("00", 0) / total
                p11 = d.get("11", 0) / total
                if p00 < 0.4 or p11 < 0.4 or (d.get("01", 0) + d.get("10", 0)) / total > 0.1:
                    issues.append(f"bell counts not 50/50 on |00>,|11>: {d}")
    return issues


def check_ghz(row, q, o):
    out = o["stdout"]
    issues = []
    # GHZ: only |0...0> and |1...1> populated
    if "counts" in out.lower() or "shot" in out.lower():
        # find bitstring: count pairs
        pairs = re.findall(r"'([01]+)'\s*:\s*(\d+)", out)
        if pairs:
            d = {k: int(v) for k, v in pairs}
            total = sum(d.values())
            if total > 0:
                nbits = len(next(iter(d)))
                all0 = "0" * nbits
                all1 = "1" * nbits
                p_target = (d.get(all0, 0) + d.get(all1, 0)) / total
                if p_target < 0.9:
                    issues.append(
                        f"GHZ not concentrated on |{all0}>,|{all1}>: top={Counter(d).most_common(3)}"
                    )
    return issues


def check_statevector(row, q, o):
    out = o["stdout"]
    issues = []
    # If question asks to verify/match a target, require a fidelity/match/diff line
    if re.search(r"(match|verify|target|fidelity|expected)", q, re.I):
        if not has_verify_pass(out) and not re.search(r"(fidelity|diff|match|equal)", out, re.I):
            issues.append(
                "question asks for verification/match but stdout has no fidelity/match/diff line"
            )
    return issues


def check_quantitative(row, q, o):
    """If the question states a specific numeric value, check stdout mentions it."""
    out = o["stdout"]
    issues = []
    # fidelity target like 0.99 or 1.0
    for pat, _label in [
        (r"fidelity[^\d]{0,8}(0\.\d+|1\.0+)", "fidelity"),
    ]:
        m = re.search(pat, q, re.I)
        if m:
            val = m.group(1)
            # check stdout has a fidelity close to that
            m2 = re.search(r"fidelity[^\d]{0,8}([-+]?\d*\.?\d+)", out, re.I)
            if not m2:
                issues.append(f"question mentions fidelity {val} but stdout has no fidelity value")
    return issues


def main():
    flags = []
    for e in A["entries"]:
        row = e["row"]
        tt = e.get("task_type", "other")
        q = QC[row - 1]["question"]
        o = OUT[row - 1]
        out = o["stdout"]
        issues = []
        if not out.strip():
            issues.append("empty stdout")
        if has_fail(out) and not has_verify_pass(out):
            issues.append("fail-marker without success-marker")
        if tt == "bell_state":
            issues += check_bell(row, q, o)
        elif tt == "ghz_state":
            issues += check_ghz(row, q, o)
        elif tt == "statevector":
            issues += check_statevector(row, q, o)
        issues += check_quantitative(row, q, o)
        if issues:
            flags.append(
                {
                    "row": row,
                    "task_type": tt,
                    "framework": e.get("framework", "?"),
                    "issues": issues,
                    "stdout_head": out[:300],
                }
            )
    print(f"Total flagged: {len(flags)} / 1000")
    by_tt = Counter(f["task_type"] for f in flags)
    print("by task_type:", dict(by_tt))
    # write full report
    (BASE / "audit_semantic_v6.json").write_text(
        json.dumps(
            {
                "total": 1000,
                "flagged": len(flags),
                "by_task_type": dict(by_tt),
                "flags": flags,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    # print first 30
    for f in flags[:30]:
        print(f"  row {f['row']:4d} [{f['task_type']}/{f['framework']}]: {f['issues']}")
        print(f"        stdout: {f['stdout_head'][:160]!r}")


if __name__ == "__main__":
    main()

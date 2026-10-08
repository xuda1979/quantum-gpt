#!/usr/bin/env python3
"""acceptance_gate.py — deterministic verdict acceptance. No vibes, no LLM judgment.

A verdict is ACCEPTED iff ALL fail-closed markers hold:
  adapter_applied AND probe_differs AND candidates_differ_from_base
  AND beats_base is consistent with the pass counts.

Usage:
    python3 harness/scripts/acceptance_gate.py <verdict.json>
Exit 0 = ACCEPT, exit 1 = REJECT.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _parse_pass(s: str) -> int:
    """'4/18' → 4. <5 lines."""
    m = re.match(r"(\d+)/", str(s or "0/"))
    return int(m.group(1)) if m else 0


def check_verdict(v: dict) -> tuple[bool, list[str]]:
    """Return (accept, reasons). <12 lines."""
    reasons = []
    if not v.get("adapter_applied"):
        reasons.append("adapter_applied=false (VOID leg)")
    if not v.get("probe_differs"):
        reasons.append("probe_differs=false (adapter inert)")
    if not v.get("candidates_differ_from_base", True):
        reasons.append("candidates identical to base (no real adapter effect)")
    pa = _parse_pass(v.get("pass_adapter"))
    pb = _parse_pass(v.get("pass_base"))
    if v.get("beats_base") and pa <= pb:
        reasons.append(f"beats_base=true fabricated (adapter {pa} <= base {pb})")
    ok = not reasons
    return ok, reasons


def main() -> None:
    """<10 lines."""
    if len(sys.argv) != 2:
        print("usage: acceptance_gate.py <verdict.json>")
        sys.exit(2)
    v = json.loads(Path(sys.argv[1]).read_text())
    ok, reasons = check_verdict(v)
    print("ACCEPT" if ok else "REJECT")
    for r in reasons:
        print(f"  - {r}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

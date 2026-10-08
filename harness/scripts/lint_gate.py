#!/usr/bin/env python3
"""lint_gate.py — hygiene gate: stray files, config drift, doc staleness.

Fails when:
  - stray files sit in harness/state/ root (probes/reports belong in subdirs)
  - stray files sit in .sapo-loop/ root (notes belong in their files)
  - lane docs are stale vs harness/contracts.py (regenerate: contracts.py generate)
  - ports are re-declared in scripts instead of importing harness_config

Exit 0 = clean. CI + pre-commit + agents run this; one line of output per issue.

Usage:
    python3 harness/scripts/lint_gate.py
    python3 harness/scripts/lint_gate.py --fix   # remove approved strays
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
from contracts import LANES, LANE_FILES, render_lane_md, LANES_DIR  # noqa: E402

# State dirs: subdirs are FINE (state/probes, state/briefs); ROOT files must
# match this allowlist (state files scripts write deterministically).
STATE_ALLOW = re.compile(
    r"^("
    r"[A-Z][A-Z0-9_]+\.json|"
    r"[a-z0-9_]+(_state)?\.json|"
    r".*\.md|"
    r".*\.lock|"
    r"eval_watcher\.json|"
    r"checkpoint_publisher\.json|"
    r"EVENTS\.jsonl|"
    r"tick\.log|"
    r"launchd-.*\.log|"  # live qgh tick daemon stdout
    r"\.gitignore"
    r")$"
)
# .sapo-loop: .md docs + dotfiles + json state are the workflow; everything
# else (probes, scratch scripts, logs, txt) is token-tax stray.
SAPO_ALLOW = re.compile(
    r"^([A-Za-z0-9_\-]+\.md|\.[a-z_]+|[a-z0-9_]+\.json|[A-Z0-9_]+\.md|[a-z0-9_]+\.lock|[a-z0-9_]+\.jsonl)$"
)
SCRATCH = REPO / "scratch"

PORT_REDECL = re.compile(r"BOX_PORTS\s*=\s*\{")
PORTS_LINE = "from harness_config import get"


def lint_state() -> list[str]:
    """Stray files in harness/state root. <8 lines."""
    issues = []
    for p in (REPO / "harness" / "state").iterdir():
        if p.is_file() and not STATE_ALLOW.match(p.name):
            issues.append(f"stray-state: {p.relative_to(REPO)} -> move to scratch/ or a state subdirectory")
    return issues


def lint_sapo() -> list[str]:
    """Stray files in .sapo-loop root. <8 lines."""
    sapo = REPO / ".sapo-loop"
    if not sapo.exists():
        return []
    issues = []
    for p in sapo.iterdir():
        if p.is_file() and not SAPO_ALLOW.match(p.name):
            issues.append(f"stray-sapo: {p.relative_to(REPO)} -> scratch/ (gitignored)")
    return issues


def lint_docs() -> list[str]:
    """Generated lane docs stale vs contracts. <8 lines."""
    issues = []
    for lane_id in LANES:
        path = LANES_DIR / LANE_FILES[lane_id]
        if not path.exists() or path.read_text() != render_lane_md(lane_id):
            issues.append(f"stale-doc: {path.relative_to(REPO)} -> run: python3 harness/contracts.py generate")
    return issues


def lint_ports() -> list[str]:
    """Ports re-declared in harness scripts. <10 lines."""
    issues = []
    for p in sorted((REPO / "harness" / "scripts").glob("*.py")):
        text = p.read_text()
        if PORT_REDECL.search(text) and "harness_config" not in text:
            issues.append(f"port-drift: {p.name} re-declares BOX_PORTS -> import harness_config.get('box_ports')")
    return issues


def run_all() -> list[str]:
    """All checks. <5 lines."""
    return lint_state() + lint_sapo() + lint_docs() + lint_ports()


def main() -> None:
    """One issue per line; exit 1 on any. <8 lines."""
    ap = argparse.ArgumentParser(description="Hygiene lint gate")
    ap.add_argument("--fix", action="store_true", help="auto-regen stale lane docs")
    args = ap.parse_args()
    issues = run_all()
    if args.fix:
        subprocess.run([sys.executable, str(REPO / "harness/contracts.py"), "generate"], check=False)
        issues = run_all()
    for i in issues:
        print(f"LINT: {i}")
    print(f"CLEAN: {len(issues)} issues" if not issues else f"{len(issues)} ISSUES")
    sys.exit(0 if not issues else 1)


if __name__ == "__main__":
    main()

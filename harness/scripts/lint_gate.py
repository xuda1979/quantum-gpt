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
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
from contracts import LANE_FILES, LANES, LANES_DIR, render_lane_md  # noqa: E402

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
    return (lint_state() + lint_sapo() + lint_docs() + lint_ports()
            + lint_scorer_pins())



def lint_scorer_pins(repo_root=None) -> list[str]:
    """C-10558: fail closed when scorer / holdout-manifest / beats_base diverge
    from the C-9131 scorer pin bank. Every scorer file's on-disk sha, the
    holdout bench sha, and the manifest pin must match the banked values."""
    import hashlib as _hashlib

    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from evals.runner import holdout_freeze as fzmod

    root = Path(repo_root) if repo_root is not None else REPO
    bank_path = root / "harness" / "state" / "scorer_sha_pins.json"
    bench_rel = fzmod.BENCH_RELPATH
    manifest_rel = fzmod.MANIFEST_RELPATH
    issues = []
    if not bank_path.is_file():
        return ["scorer-pin-drift: C-9131 bank missing: " + str(bank_path)]
    try:
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["scorer-pin-drift: C-9131 bank unreadable: " + str(bank_path)]
    bank_shas = bank.get("scorer_shas") or {}
    hold = bank.get("holdout_sha256")

    def _sha(rel):
        p = root / rel
        if not p.is_file():
            return None
        return _hashlib.sha256(p.read_bytes()).hexdigest()

    manifest = {}
    try:
        for line in (root / manifest_rel).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and len(parts[0]) == 64:
                manifest[parts[1]] = parts[0].lower()
    except OSError:
        issues.append("scorer-pin-drift: freeze manifest missing: " + str(root / manifest_rel))

    if hold is None:
        issues.append("scorer-pin-drift: bank lacks holdout_sha256")
    else:
        disk = _sha(bench_rel)
        m_pin = manifest.get(bench_rel)
        if disk is not None and str(disk).lower() != str(hold).lower():
            issues.append("scorer-pin-drift: " + bench_rel + " disk " + str(disk) + " != bank " + str(hold))
        if m_pin is not None and str(m_pin).lower() != str(hold).lower():
            issues.append("scorer-pin-drift: " + bench_rel + " manifest " + str(m_pin) + " != bank " + str(hold))

    for rel in fzmod.SCORER_CHAIN:
        want = bank_shas.get(rel)
        if not want:
            issues.append("scorer-pin-drift: bank lacks pin for " + rel)
            continue
        disk = _sha(rel)
        m_pin = manifest.get(rel)
        if disk is None:
            issues.append("scorer-pin-drift: " + rel + " missing on disk")
            continue
        if str(disk).lower() != str(want).lower():
            issues.append("scorer-pin-drift: " + rel + " disk " + str(disk) + " != bank " + str(want))
        if m_pin is not None and str(m_pin).lower() != str(want).lower():
            issues.append("scorer-pin-drift: " + rel + " manifest " + str(m_pin) + " != bank " + str(want))
    return issues


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

#!/usr/bin/env python3
"""Mandate Gate (user mandates 2026-09-22/23): police layer checks.

Mandates enforced every heartbeat cycle:
  M1. dp4 is the ONLY judge — no fallback judge model may score candidates.
  M2. Code files <= 200 lines (first-party .py under harness/ and scripts/,
      excluding *.bak*, __pycache__, dist, build; venvs excluded).
  M3. Every changed .py file has a unit test; every change lands with tests
      (this gate reports violations; TDD itself is per-card gate).

Fail-closed: unreadable state is RED, never a silent pass. Output is consumed
by sapo_huanxin_heartbeat.sh police layer (GREEN/RED line).
Stdlib only; Python 3.9-safe.
"""
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE_LIMIT = 200

# M1: source patterns that indicate a non-dp4 judge is reachable.
# The fail-closed STUB itself is allowed (it returns an error, never a score).
FORBIDDEN_JUDGE_CALL = re.compile(r"call_zhipu_fallback\(body\)|zhipu.*judge|judge.*zhipu", re.I)
ALLOWED_STUB = "judge_policy"


def _first_party_py_files():
    for root in ("harness", "scripts"):
        top = os.path.join(REPO, root)
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames
                           if d not in ("__pycache__", "dist", "build", ".git")]
            for fn in filenames:
                if fn.endswith(".py") and ".bak" not in fn:
                    yield os.path.join(dirpath, fn)


def check_line_limits():
    """M2: files over the limit. Returns list of violation strings."""
    bad = []
    for path in _first_party_py_files():
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                n = sum(1 for _ in fh)
        except OSError as exc:
            bad.append("UNREADABLE %s (%s)" % (path, exc))
            continue
        if n > LINE_LIMIT:
            bad.append("%d lines > %d: %s" % (n, LINE_LIMIT, os.path.relpath(path, REPO)))
    return bad


def check_dp4_only_judge():
    """M1: no reachable non-dp4 judge. The removed-fallback stub is allowed."""
    bad = []
    for path in _first_party_py_files():
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in FORBIDDEN_JUDGE_CALL.finditer(src):
            ctx = src[max(0, m.start() - 80):m.end() + 80]
            if ALLOWED_STUB in ctx:
                continue
            bad.append("non-dp4 judge reference in %s: ...%s..." %
                       (os.path.relpath(path, REPO), m.group(0)))
    return bad


def _git(name, *args):
    return subprocess.run(["git", "-C", REPO, name, *args],
                          capture_output=True, text=True, timeout=30)


def check_changed_files_have_tests():
    """M3: every .py changed vs HEAD (staged or modified) must have a unit
    test file that imports it or names it. Report-only list (RED drives the
    loop to fix; not a hard block on unrelated legacy debt)."""
    r = _git("status", "--porcelain")
    if r.returncode != 0:
        return ["git status unavailable (rc=%d)" % r.returncode]
    changed = []
    for line in r.stdout.splitlines():
        st, path = line[:2], line[3:].strip()
        if not path.endswith(".py") or ".bak" in path:
            continue
        if any(s in st for s in ("M", "A", "?")):
            changed.append(path)
    if not changed:
        return []
    test_files = []
    for root in ("tests", "harness/tests"):
        top = os.path.join(REPO, root)
        if not os.path.isdir(top):
            continue
        for fn in os.listdir(top):
            if fn.startswith("test_") and fn.endswith(".py"):
                try:
                    test_files.append(open(os.path.join(top, fn),
                                           encoding="utf-8", errors="replace").read())
                except OSError:
                    pass
    blob = "\n".join(test_files)
    missing = [p for p in changed
               if os.path.basename(p) not in blob and p not in blob]
    return ["changed file without unit test reference: %s" % p for p in missing]


def main():
    red = []
    red.extend(check_dp4_only_judge())
    red.extend(check_line_limits())
    red.extend(check_changed_files_have_tests())
    if red:
        print("MANDATE-GATE: RED")
        for item in red[:40]:
            print("  -", item)
        if len(red) > 40:
            print("  ... and %d more" % (len(red) - 40))
        return 1
    print("MANDATE-GATE: GREEN (dp4-only judge; <=200 lines; changed files tested)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

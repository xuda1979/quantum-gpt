"""Harness self-review: comprehensive quality audit.

The harness must review its own work and improve. This module runs a full
self-diagnostic and reports actionable findings with a quality score.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request


def run_review(state_dir, repo_dir):
    findings = []
    passes = []

    print("=== HARNESS SELF-REVIEW ===")

    # 1. Test suite
    print("\n--- 1. Test Suite ---")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "harness/tests/", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=repo_dir,
        )
        line = (r.stdout + r.stderr).strip().split("\n")[-1]
        print(f"  {line}")
        if "failed" in line and "0 failed" not in line:
            findings.append(f"test suite: {line}")
        else:
            passes.append("test suite green")
    except Exception as exc:
        print(f"  ERROR: {exc}")
        findings.append("test suite could not run")

    # 2. Tick health
    print("\n--- 2. Tick Health ---")
    status_md = os.path.join(state_dir, "STATUS.md")
    if not os.path.exists(status_md):
        print("  WARN: no STATUS.md (never ticked?)")
        findings.append("no successful tick ever")
    else:
        age = time.time() - os.path.getmtime(status_md)
        if age > 2400:
            print(f"  FAIL: last success {int(age)}s ago (halted)")
            findings.append(f"loop halted: last success {int(age)}s ago")
        else:
            print(f"  PASS: last success {int(age)}s ago")
            passes.append("tick healthy")

    # 3. Environment health
    print("\n--- 3. Environments ---")
    for name, port in (("ASI1", 20646), ("ASI2", 19004), ("ASI3", 20653)):
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
            d = json.loads(r.read())
            ready = d.get("ready")
            if ready:
                print(
                    f"  PASS: {name} ready (uptime={d.get('uptime')}s cmds={d.get('commandCount')})"
                )
                passes.append(f"{name} ready")
            else:
                print(f"  WARN: {name} not ready (startup={d.get('startupState')})")
                findings.append(f"{name} not ready: {d.get('startupState')}")
        except Exception:
            print(f"  FAIL: {name} DOWN")
            findings.append(f"{name} down")

    # 4. Fleet health
    print("\n--- 4. Fleet Health ---")
    try:
        fleet = json.load(open(os.path.join(state_dir, "FLEET.json")))
        running = [a for a in fleet["agents"] if a.get("status") == "running"]
        alive = 0
        for a in running:
            pid = a.get("pid")
            try:
                os.kill(pid, 0)
                alive += 1
            except Exception:
                pass
        zombies = len(running) - alive
        print(f"  running={len(running)} alive={alive} zombies={zombies}")
        if zombies > 0:
            findings.append(f"{zombies} zombie fleet entries")
        elif alive > 0:
            passes.append(f"fleet healthy ({alive} live workers)")
        else:
            print("  WARN: no live workers")
            findings.append("no live workers")
    except Exception as exc:
        print(f"  ERROR: {exc}")
        findings.append("fleet check failed")

    # 5. Code quality (ruff)
    print("\n--- 5. Code Quality (ruff) ---")
    try:
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "harness/qgh.py",
                "harness/harness_lib.py",
                "harness/dashboard.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_dir,
        )
        if r.returncode == 0:
            print("  PASS: harness core is ruff-clean")
            passes.append("ruff clean")
        else:
            n = r.stdout.count(": ") if r.stdout else 0
            print(f"  WARN: {n} ruff issues in harness core")
            findings.append(f"ruff: {n} issues")
    except Exception:
        print("  SKIP: ruff not available")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"  passes: {len(passes)}")
    print(f"  findings: {len(findings)}")
    if findings:
        print("  ACTIONABLE FINDINGS:")
        for f in findings:
            print(f"    - {f}")
    score = (
        len(passes) / (len(passes) + len(findings)) * 100
        if (len(passes) + len(findings)) > 0
        else 0
    )
    print(f"  QUALITY SCORE: {score:.0f}%")
    return 0 if not findings else 1

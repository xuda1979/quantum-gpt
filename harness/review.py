"""Harness self-review: comprehensive quality audit.

The harness must review its own work and improve. This module runs a full
self-diagnostic and reports actionable findings with a quality score.
"""

import inspect
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

    # 5. Goal status check
    print("\n--- 5. Goal Status ---")
    try:
        goal_path = os.path.join(state_dir, "GOAL.json")
        if os.path.exists(goal_path):
            with open(goal_path) as f:
                goal = json.load(f)
            status = goal.get("status", "UNKNOWN")
            target = goal.get("target_pass", "18/18")
            print(f"  Goal: {status} (target: {target})")
            if status == "OPEN":
                passes.append("goal is OPEN (still pursuing 18/18)")
            elif status == "DONE":
                findings.append("goal is DONE -- harness should stop")
        else:
            findings.append("GOAL.json missing -- harness not initialized")
    except Exception as exc:
        findings.append(f"goal check error: {exc}")

    # 6. Queue health check
    print("\n--- 6. Queue Health ---")
    try:
        queue_path = os.path.join(state_dir, "QUEUE.json")
        if os.path.exists(queue_path):
            with open(queue_path) as f:
                queue = json.load(f)
            cards = queue.get("cards", [])
            statuses = {}
            for c in cards:
                s = c.get("status", "?")
                statuses[s] = statuses.get(s, 0) + 1
            print(f"  Cards: {statuses}")
            bounced = statuses.get("bounced", 0)
            running = statuses.get("running", 0)
            ready = statuses.get("ready", 0)
            if bounced > 6:
                findings.append(f"high bounce count: {bounced} bounced cards need decomposition")
            else:
                passes.append(f"bounce count manageable: {bounced}")
            if running == 0 and ready == 0:
                findings.append("no active or ready cards -- harness may be stalled")
            else:
                passes.append(f"active queue: {running} running, {ready} ready")
    except Exception as exc:
        findings.append(f"queue check error: {exc}")

    # 7. Tick automation wiring check
    print("\n--- 7. Automation Wiring ---")
    try:
        harness_dir = os.path.join(repo_dir, "harness")
        if harness_dir not in sys.path:
            sys.path.insert(0, harness_dir)
        import qgh  # noqa: E402

        tick_src = inspect.getsource(qgh.cmd_tick)
        checks = [
            ("auto_queue_training", "auto_queue_training(" in tick_src),
            ("auto_eval_scan", "auto_eval_scan(" in tick_src),
            ("auto_requeue_zero_bounce", "auto_requeue_zero_bounce(" in tick_src),
        ]
        for name, wired in checks:
            if wired:
                print(f"  PASS: {name} wired into tick")
                passes.append(f"{name} wired")
            else:
                print(f"  FAIL: {name} NOT wired into tick")
                findings.append(f"{name} not called from cmd_tick")
    except Exception as exc:
        findings.append(f"automation wiring check error: {exc}")

    # 8. Last successful tick age
    print("\n--- 8. Tick Liveness ---")
    try:
        status_path = os.path.join(state_dir, "STATUS.md")
        if os.path.exists(status_path):
            age_s = time.time() - os.path.getmtime(status_path)
            age_min = age_s / 60.0
            print(f"  Last successful tick: {age_min:.1f} min ago")
            if age_min > 60:
                findings.append(f"tick HALTED: no success in {age_min:.0f} min")
            else:
                passes.append(f"tick recent: {age_min:.0f} min ago")
        else:
            findings.append("STATUS.md missing -- no successful tick ever")
    except Exception as exc:
        findings.append(f"tick liveness check error: {exc}")

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

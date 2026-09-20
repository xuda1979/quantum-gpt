#!/usr/bin/env python3
"""Run every reference solution and verify it produces the expected substrings."""
import json, subprocess, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
PROBLEMS = json.loads((RUN / "PROBLEMS.json").read_text())
results = []
for p in PROBLEMS:
    ref = RUN / "reference" / f"{p['id']}.py"
    try:
        out = subprocess.run([sys.executable, str(ref)], capture_output=True,
                             text=True, timeout=p["timeout"])
        ok = out.returncode == 0 and all(s in out.stdout for s in p["expected_substrings"])
        results.append((p["id"], ok, out.stdout, out.stderr))
    except subprocess.TimeoutExpired:
        results.append((p["id"], False, "", "TIMEOUT"))
    except Exception as e:
        results.append((p["id"], False, "", str(e)))

passed = sum(1 for _, ok, _, _ in results if ok)
print(f"\n=== Reference verification: {passed}/{len(results)} passed ===\n")
for pid, ok, stdout, stderr in results:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {pid}")
    if not ok:
        print(f"  stdout: {stdout[-400:]}")
        print(f"  stderr: {stderr[-400:]}")

# Write to file
(RUN / "logs" / "reference_check.txt").write_text(
    f"Reference verification: {passed}/{len(results)}\n\n" +
    "\n".join(f"[{'PASS' if ok else 'FAIL'}] {pid}\n{('  stdout: ' + stdout[-400:] + chr(10) + '  stderr: ' + stderr[-400:]) if not ok else ''}"
              for pid, ok, stdout, stderr in results)
)

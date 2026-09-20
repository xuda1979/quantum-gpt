#!/usr/bin/env python3
"""Verify reference for quantum_grover_3sat_4var produces expected output."""
import subprocess, sys
from pathlib import Path
REF = Path(__file__).resolve().parent.parent / "reference" / "quantum_grover_3sat_4var.py"
EXPECTED = ['Satisfying count = 2', 'Most likely = ', 'Valid: ', 'Peak prob = ']
TIMEOUT = 120
def main():
    try:
        out = subprocess.run([sys.executable, str(REF)], capture_output=True,
                             text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print({"status": "TIMEOUT", "task_id": "quantum_grover_3sat_4var", "detail": "timed out"})
        return
    stdout = out.stdout
    ok = all(s in stdout for s in EXPECTED)
    if ok:
        print({"status": "PASS", "task_id": "quantum_grover_3sat_4var", "detail": stdout[-200:]})
    else:
        missing = [s for s in EXPECTED if s not in stdout]
        print({"status": "FAIL", "task_id": "quantum_grover_3sat_4var",
               "detail": "missing: " + ", ".join(missing) + " | stdout: " + stdout[-300:] + " | stderr: " + out.stderr[-300:]})
if __name__ == "__main__":
    main()

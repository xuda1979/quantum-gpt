#!/usr/bin/env python3
"""Verify reference for quantum_amplitude_estimation_3bit produces expected output."""
import subprocess, sys
from pathlib import Path
REF = Path(__file__).resolve().parent.parent / "reference" / "quantum_amplitude_estimation_3bit.py"
EXPECTED = ['Target amplitude = 0.1464', 'Estimated amplitude = ', 'Abs error = ', 'Converged: ']
TIMEOUT = 120
def main():
    try:
        out = subprocess.run([sys.executable, str(REF)], capture_output=True,
                             text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print({"status": "TIMEOUT", "task_id": "quantum_amplitude_estimation_3bit", "detail": "timed out"})
        return
    stdout = out.stdout
    ok = all(s in stdout for s in EXPECTED)
    if ok:
        print({"status": "PASS", "task_id": "quantum_amplitude_estimation_3bit", "detail": stdout[-200:]})
    else:
        missing = [s for s in EXPECTED if s not in stdout]
        print({"status": "FAIL", "task_id": "quantum_amplitude_estimation_3bit",
               "detail": "missing: " + ", ".join(missing) + " | stdout: " + stdout[-300:] + " | stderr: " + out.stderr[-300:]})
if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify reference for quantum_bayesian_inference_3var produces expected output."""
import subprocess, sys
from pathlib import Path
REF = Path(__file__).resolve().parent.parent / "reference" / "quantum_bayesian_inference_3var.py"
EXPECTED = ['P(A=1) = 0.3000', 'P(C=1) = ', 'P(A=1|C=1) = ', 'Quantum P(A=1|C=1) = ', 'Match: ']
TIMEOUT = 120
def main():
    try:
        out = subprocess.run([sys.executable, str(REF)], capture_output=True,
                             text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print({"status": "TIMEOUT", "task_id": "quantum_bayesian_inference_3var", "detail": "timed out"})
        return
    stdout = out.stdout
    ok = all(s in stdout for s in EXPECTED)
    if ok:
        print({"status": "PASS", "task_id": "quantum_bayesian_inference_3var", "detail": stdout[-200:]})
    else:
        missing = [s for s in EXPECTED if s not in stdout]
        print({"status": "FAIL", "task_id": "quantum_bayesian_inference_3var",
               "detail": "missing: " + ", ".join(missing) + " | stdout: " + stdout[-300:] + " | stderr: " + out.stderr[-300:]})
if __name__ == "__main__":
    main()

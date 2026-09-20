# Auto-generated from distillation reference (row qc-0472).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Matrix A:\n[[1.5 0.5]\n[0.5 1.5]]\nVector b: [1. 0.]\n\nEigenvalues of A: [1. 2.]\nEigenvectors of A:\n[[-0.70710678 0.70710678]\n[ 0.70710678 0.70710678]]\n\nExact solution x: [ 0.75 -0.25]\nExact normalized solution: [ 0.9486833 -0.31622777]\n\nHHL measurement counts (ancilla=1):\nb=0 count: 0\nb=1 count: 0\ntotal success count: 0\nsuccess probability: 0.0\n\nHHL normalized solution (from sqrt of probabilities): [0. 0.]\nExact normalized solution: [ 0.9486833 -0.31622777]\nAbsolute difference: [0.9486833 0.31622777]\nFidelity: 0.0'


def _normalize(text):
    # collapse whitespace runs; strip trailing spaces per line
    lines = []
    for line in text.splitlines():
        lines.append(" ".join(line.split()))
    return "\n".join(lines).strip()


def run_tests(candidate_path: str) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, candidate_path],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "details": ["candidate timed out (> 120s)"]}
    if proc.returncode != 0:
        return {
            "passed": False,
            "details": ["exit code {r}" .format(r=proc.returncode) + ": " + proc.stderr.strip()[:500]],
        }
    actual = _normalize(proc.stdout)
    if actual == EXPECTED:
        return {"passed": True, "details": ["stdout matches reference"]}
    return {
        "passed": False,
        "details": [
            "stdout mismatch",
            "expected: " + EXPECTED[:200],
            "actual:   " + actual[:200],
        ],
    }

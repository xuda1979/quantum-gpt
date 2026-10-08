# Auto-generated from distillation reference (row qc-0699).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Matrix A:\n[[2. 1.]\n[1. 2.]]\n\nVector b:\n[1. 0.]\n\nExact solution (numpy.linalg.solve):\n[ 0.66666667 -0.33333333]\n\nExact normalized solution:\n[ 0.89442719 -0.4472136 ]\n\nEigenvalues of A: [1. 3.]\nEigenvectors of A:\n[[-0.70710678 0.70710678]\n[ 0.70710678 0.70710678]]\n\nHHL measurement probabilities (post-selected on ancilla=0):\nP(b=0 | anc=0) = 0.0000\nP(b=1 | anc=0) = 0.0000\n\nHHL reconstructed normalized solution:\n[0. 0.]\n\nComparison (absolute differences):\n|x_hhl[0] - x_exact_norm[0]| = 0.8944\n|x_hhl[1] - x_exact_norm[1]| = 0.4472\n\nAncilla=0 success probability: 0.0000'


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

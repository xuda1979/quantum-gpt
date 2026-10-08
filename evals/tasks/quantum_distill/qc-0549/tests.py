# Auto-generated from distillation reference (row qc-0549).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Random 2D points X:\n[[1.15255478 4.89894304]\n[3.75012014 2.8012498 ]\n[0.62816092 2.88554589]\n[2.09675304 0.89765869]\n[4.08965289 0.3544444 ]]\n\nKernel matrix K:\n[[1. 0.0209969 0.14215655 0.00425798 0.00594622]\n[0.0209969 1. 0.4377751 0.02934966 0.73892327]\n[0.14215655 0.4377751 1. 0.27973693 0.19746953]\n[0.00425798 0.02934966 0.27973693 1. 0.00618486]\n[0.00594622 0.73892327 0.19746953 0.00618486 1. ]]\n\nMax |K - K^T| (symmetry check): 4.440892098500626e-16\nMax |diag(K) - 1| (unit diagonal check): 2.4424906541753444e-15\n\nVerification PASSED: K is symmetric with unit diagonal.'


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

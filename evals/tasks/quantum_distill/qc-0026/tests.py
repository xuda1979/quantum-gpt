# Auto-generated from distillation reference (row qc-0026).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Random 2D points (features):\n[[2.35330497 5.97351416]\n[4.59925358 3.76148219]\n[0.98029403 0.98014248]\n[0.3649501 5.44234523]]\n\nKernel matrix K:\n[[1. 0.10075845 0.33790322 0.6744723 ]\n[0.10075845 1. 0.05425894 0.25891832]\n[0.33790322 0.05425894 1. 0.12440095]\n[0.6744723 0.25891832 0.12440095 1. ]]\n\nMax |K - K^T|: 1.53e-16\nMax |diag(K) - 1|: 4.44e-16\n\nVerification PASSED: K is symmetric with unit diagonal.'


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

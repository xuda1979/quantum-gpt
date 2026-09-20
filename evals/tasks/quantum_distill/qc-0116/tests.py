# Auto-generated from distillation reference (row qc-0116).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Kernel matrix K:\n[[1. 0.10075845 0.33790322 0.6744723 0.21242307]\n[0.10075845 1. 0.05425894 0.25891832 0.71208142]\n[0.33790322 0.05425894 1. 0.12440095 0.07787954]\n[0.6744723 0.25891832 0.12440095 1. 0.61444782]\n[0.21242307 0.71208142 0.07787954 0.61444782 1. ]]\n\nSymmetric check (max |K - K.T|): 3.3306690738754696e-16\nUnit diagonal check (max |diag(K) - 1|): 4.440892098500626e-16'


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

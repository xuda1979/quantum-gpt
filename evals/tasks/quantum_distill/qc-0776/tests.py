# Auto-generated from distillation reference (row qc-0776).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Optimized parameters (gammas, betas): [2.57931887 0.6840067 0.67452799 0.41756563]\nOptimized expected cost: 3.999999858126788\n\nMeasurement probabilities:\n0011: 0.166667 (cut=4)\n0101: 0.166667 (cut=4)\n0110: 0.166667 (cut=4)\n1001: 0.166667 (cut=4)\n1010: 0.166667 (cut=4)\n1100: 0.166667 (cut=4)\n\nMost likely bitstring: 0110\nMaxCut value: 4'


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

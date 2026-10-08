# Auto-generated from distillation reference (row qc-0632).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Circuit:\n0: ───@───\n│\n1: ───@───\n│\n2: ───X───\n\nFinal state vector:\n[0. +0.j 0. +0.j 0. +0.j\n0. +0.j 0. +0.j 0. +0.j\n0. +0.j 0.70710677+0.70710677j]\n\nVerification passed:\nProbability of |111>: 0.9999998807907104\nRelative phase factor: (0.7071067690849304+0.7071067690849304j)\nExpected phase factor: (0.7071067811865476+0.7071067811865475j)'


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

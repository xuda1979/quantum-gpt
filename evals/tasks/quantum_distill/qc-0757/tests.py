# Auto-generated from distillation reference (row qc-0757).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '--- QUBO / Simulated Annealing Result ---\nSelected items (0-indexed): [0, 4]\nTotal value: 23\nTotal weight: 10\nSlack used: 0\nConstraint: weight + slack = 10 (capacity = 10)\nFeasible: True\n\n--- Brute Force Result ---\nSelected items (0-indexed): [0, 4]\nTotal value: 23\nTotal weight: 10\n\n--- Comparison ---\nMATCH: QUBO solution matches brute-force optimum.'


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

# Auto-generated from distillation reference (row qc-0540).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== 0/1 Knapsack via Penalized QUBO (Slack-Variable Encoding) ===\nValues: [12, 3, 9, 10, 9, 4]\nWeights: [3, 7, 5, 4, 6, 2]\nCapacity: 10\nSlack bits: [1, 2, 4] (encoding 0..7)\nPenalty P: 73\n\n------------------------------------------------------------\nQUBO / Simulated Annealing Result\n------------------------------------------------------------\nSelected items (0-indexed): [0, 3, 5]\nTotal value: 26\nTotal weight: 9\nSlack used: 1\nConstraint: weight + slack = 10 (capacity = 10)\nFeasible: True\n\n------------------------------------------------------------\nBrute Force Result\n------------------------------------------------------------\nSelected items (0-indexed): [0, 3, 5]\nTotal value: 26\nTotal weight: 9\n\n------------------------------------------------------------\nComparison\n------------------------------------------------------------\nMATCH: QUBO found the optimal feasible solution.\n============================================================'


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

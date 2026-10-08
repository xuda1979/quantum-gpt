# Auto-generated from distillation reference (row qc-0257).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== 0/1 Knapsack via Penalized QUBO (Slack-Variable Encoding) ===\nValues: [12, 7, 12, 2, 6, 9]\nWeights: [1, 7, 3, 3, 1, 6]\nCapacity: 10\n\nQUBO construction:\nNumber of item variables (x): 6\nSlack bits: [1, 2, 4, 8]\nNumber of slack variables: 4\nTotal QUBO variables: 10\nPenalty coefficient P: 24.0\n\nSimulatedAnnealingSampler results:\nBest energy: 0.0\nSelected items: []\nTotal value: 0\nTotal weight: 0\nSlack value: 0\nConstraint check: weight + slack = 0 (should equal 10)\nFeasible: False\n\nBrute-force results:\nOptimal selection: [0, 2, 5]\nOptimal value: 33\nOptimal weight: 10\n\nComparison:\nQUBO value: 0\nBrute-force value: 33\nMatch: False'


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

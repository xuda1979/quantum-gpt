# Auto-generated from distillation reference (row qc-0391).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== 0/1 Knapsack via Penalized QUBO (slack-variable encoding) ===\nItems: 4 | Values: [10, 10, 6, 11] | Weights: [6, 5, 3, 8] | Capacity: 10\nSlack bits: 4 (coefficients [1, 2, 4, 8])\nPenalty P: 22.0\n\n--- QUBO / Simulated Annealing Result ---\nBest energy: -1304.0\nSelected items: [2]\nTotal value: 6\nTotal weight: 3\nSlack value: 3\nWeight + Slack: 6 (capacity 10)\nFeasible: False\n\n--- Brute Force Result ---\nSelected items: [1, 2]\nTotal value: 16\nTotal weight: 8\n\n--- Comparison ---\nQUBO matches brute force optimum: False'


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

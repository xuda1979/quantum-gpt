# Auto-generated from distillation reference (row qc-0768).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== 0/1 Knapsack via Penalized QUBO (Slack-Variable Encoding) ===\nItems: 6 | Capacity: 8\nValues: [5, 4, 2, 6, 10, 4]\nWeights: [2, 7, 8, 1, 7, 8]\nSlack bits: 4 (max representable slack: 15)\nPenalty P: 21\n\n--- QUBO / Simulated Annealing ---\nSelected items: [3, 4]\nTotal value: 16\nTotal weight: 8\nFeasible: True\n\n--- Brute Force ---\nSelected items: [3, 4]\nTotal value: 16\nTotal weight: 8\n\n--- Comparison ---\nMATCH: QUBO solution equals brute-force optimum.'


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

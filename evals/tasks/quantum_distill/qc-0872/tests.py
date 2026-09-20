# Auto-generated from distillation reference (row qc-0872).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== 0/1 Knapsack via Penalized QUBO (Slack-Variable Encoding) ===\nValues: [8, 5, 9, 7]\nWeights: [6, 4, 2, 4]\nCapacity: 10\nSlack bits: 4 (values [1, 2, 4, 8])\nPenalty A: 18, Objective scale B: 1\n\n--- QUBO (SimulatedAnnealingSampler) ---\nSelected items (0-indexed): []\nTotal weight: 0\nTotal value: 0\nQUBO energy: -1800.0\n\n--- Brute Force ---\nSelected items (0-indexed): [1, 2, 3]\nTotal weight: 10\nTotal value: 21\n\nMatch: False'


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

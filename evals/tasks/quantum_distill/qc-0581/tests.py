# Auto-generated from distillation reference (row qc-0581).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Knapsack QUBO via Simulated Annealing ===\nItems: n=5, values=[3, 12, 2, 9, 6], weights=[3, 3, 1, 2, 1], capacity=10\nPenalty (lambda): 24\nSlack bits: 4, slack weights: [1, 2, 4, 8]\nQUBO variables: 9 (5 item + 4 slack)\n\n--- Simulated Annealing Result ---\nBest energy: -2837.0\nItem selection (x): [np.int8(0), np.int8(1), np.int8(1), np.int8(1), np.int8(1)]\nSlack bits (s): [np.int8(1), np.int8(1), np.int8(0), np.int8(0)]\nTotal weight: 7 (capacity=10)\nSlack sum: 3\nConstraint: weight + slack = 10 (should equal 10)\nTotal value: 29\n\n--- Brute Force Result ---\nOptimal selection: [1, 1, 1, 1, 1]\nOptimal weight: 10\nOptimal value: 32\n\nSA matches brute force optimum: NO'


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

# Auto-generated from distillation reference (row qc-0018).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Knapsack QUBO via Simulated Annealing ===\nItems (values): [7, 11, 9, 7, 2, 8]\nItems (weights): [3, 2, 1, 1, 3, 7]\nCapacity: 11\nPenalty: 200\nSlack weights: [1, 2, 4, 8]\nSA best energy: -35000.0\nSA selected: [np.int8(0), np.int8(0), np.int8(0), np.int8(0), np.int8(0), np.int8(0)]\nSA total weight: 0\nSA total value: 0\nSA slack bits: [np.int8(1), np.int8(1), np.int8(1), np.int8(1)] (sum=15)\nConstraint w+slack=cap: 0+15=15 (cap=11)\nBrute force best: [1, 1, 1, 1, 1, 0]\nBrute force value: 36\nBrute force weight:10\nSA matches brute force optimum: NO'


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

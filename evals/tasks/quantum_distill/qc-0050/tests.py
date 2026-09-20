# Auto-generated from distillation reference (row qc-0050).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== MaxCut QUBO via Simulated Annealing ===\nEdges: [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (1, 5), (2, 4), (2, 5), (3, 5)]\nQUBO: {(0, 0): -3, (1, 1): -4, (0, 1): 2, (4, 4): -2, (0, 4): 2, (5, 5): -4, (0, 5): 2, (2, 2): -3, (1, 2): 2, (3, 3): -2, (1, 3): 2, (1, 5): 2, (2, 4): 2, (2, 5): 2, (3, 5): 2}\nSA best sample: {0: np.int8(1), 1: np.int8(0), 2: np.int8(1), 3: np.int8(1), 4: np.int8(0), 5: np.int8(0)}\nSA energy (QUBO): -8.0\nSA cut value: 8.0\n\n=== Brute Force Verification ===\nBrute force best assignment: {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1}\nBrute force energy (QUBO): -8\nBrute force cut value: 8\n\nVERIFICATION PASSED: SA found the optimal MaxCut.'


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

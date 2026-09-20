# Auto-generated from distillation reference (row qc-0191).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 5), (3, 4), (4, 5)]\nNodes: [0, 1, 2, 3, 4, 5]\n\nQUBO matrix Q:\n(0, 0): -3\n(0, 3): 2\n(0, 4): 2\n(0, 5): 2\n(1, 1): -3\n(1, 3): 2\n(1, 4): 2\n(1, 5): 2\n(2, 2): -1\n(2, 5): 2\n(3, 3): -3\n(3, 4): 2\n(4, 4): -4\n(4, 5): 2\n(5, 5): -4\n\nSimulated Annealing result:\nBest sample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(0), 4: np.int8(0), 5: np.int8(0)}\nEnergy: -7.0\nMaxCut value (edges cut): 7\n\nBrute force result:\nBest sample: {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 1}\nEnergy: -7\nMaxCut value (edges cut): 7\n\nVerification: PASS'


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

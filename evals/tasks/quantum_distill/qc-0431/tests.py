# Auto-generated from distillation reference (row qc-0431).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 1), (0, 2), (0, 3), (0, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (4, 5)]\nQUBO: {(0, 0): -4, (1, 1): -3, (0, 1): 2, (2, 2): -3, (0, 2): 2, (3, 3): -3, (0, 3): 2, (5, 5): -3, (0, 5): 2, (1, 3): 2, (4, 4): -4, (1, 4): 2, (2, 4): 2, (2, 5): 2, (3, 4): 2, (4, 5): 2}\n\nSimulated Annealing result:\nSample: {0: np.int8(0), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(0), 5: np.int8(1)}\nEnergy: -8.0\nCut size: 8\n\nBrute force result:\nBest energy: -8\nBest cut size: 8\nNumber of optimal assignments: 2\nOptimal assignments: [{0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 1}, {0: 1, 1: 0, 2: 0, 3: 0, 4: 1, 5: 0}]\n\nSA matches brute force best cut: True'


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

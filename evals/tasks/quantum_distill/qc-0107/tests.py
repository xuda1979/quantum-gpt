# Auto-generated from distillation reference (row qc-0107).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 4), (0, 5), (1, 3), (1, 6), (2, 3), (3, 4), (3, 5), (3, 6)]\nNodes: [0, 1, 2, 3, 4, 5, 6]\n\nQUBO matrix Q:\n(0, 0): -2\n(0, 4): 2\n(0, 5): 2\n(1, 1): -2\n(1, 3): 2\n(1, 6): 2\n(2, 2): -1\n(2, 3): 2\n(3, 3): -5\n(3, 4): 2\n(3, 5): 2\n(3, 6): 2\n(4, 4): -2\n(5, 5): -2\n(6, 6): -2\n\nSimulated Annealing result:\nSample: {0: np.int8(0), 1: np.int8(1), 2: np.int8(1), 3: np.int8(0), 4: np.int8(1), 5: np.int8(1), 6: np.int8(0)}\nEnergy: -7.0\nCut size: 7\n\nBrute force result:\nBest energy: -7\nBest cut size: 7\nNumber of optimal assignments: 6\nOptimal assignments:\n{0: 0, 1: 0, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1} -> S0=[0, 1, 3], S1=[2, 4, 5, 6]\n{0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 0} -> S0=[0, 3, 6], S1=[1, 2, 4, 5]\n{0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1} -> S0=[0, 3], S1=[1, 2, 4, 5, 6]\n{0: 1, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0} -> S0=[1, 2, 4, 5, 6], S1=[0, 3]\n{0: 1, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 1} -> S0=[1, 2, 4, 5], S1=[0, 3, 6]\n{0: 1, 1: 1, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0} -> S0=[2, 4, 5, 6], S1=[0, 1, 3]\n\nVerification: PASS'


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

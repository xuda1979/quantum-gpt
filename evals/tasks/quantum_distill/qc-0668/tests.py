# Auto-generated from distillation reference (row qc-0668).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]\n\nQUBO dictionary Q:\n(0, 0): 3\n(0, 1): -2\n(0, 2): -2\n(0, 3): -2\n(1, 1): 3\n(1, 2): -2\n(1, 4): -2\n(2, 2): 4\n(2, 3): -2\n(2, 4): -2\n(3, 3): 3\n(3, 4): -2\n(4, 4): 3\n\nSimulatedAnnealingSampler result:\nSample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1)}\nEnergy: 0.0\nMaxCut value: 0\n\nBrute force result:\nSample: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}\nEnergy: 0.0\nMaxCut value: 0\n\nVerification PASSED: Simulated annealing matches brute force max cut value.'


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

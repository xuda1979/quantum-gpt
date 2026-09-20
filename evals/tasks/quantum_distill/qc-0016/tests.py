# Auto-generated from distillation reference (row qc-0016).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 4), (0, 5), (0, 6), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (3, 5), (3, 6), (4, 5), (4, 6), (5, 6)]\nNumber of nodes: 7\n\nQUBO matrix Q:\nQ[(0, 0)] = -3.0\nQ[(0, 4)] = 2.0\nQ[(0, 5)] = 2.0\nQ[(0, 6)] = 2.0\nQ[(1, 1)] = -3.0\nQ[(1, 2)] = 2.0\nQ[(1, 3)] = 2.0\nQ[(1, 4)] = 2.0\nQ[(2, 2)] = -3.0\nQ[(2, 3)] = 2.0\nQ[(2, 4)] = 2.0\nQ[(3, 3)] = -5.0\nQ[(3, 4)] = 2.0\nQ[(3, 5)] = 2.0\nQ[(3, 6)] = 2.0\nQ[(4, 4)] = -6.0\nQ[(4, 5)] = 2.0\nQ[(4, 6)] = 2.0\nQ[(5, 5)] = -4.0\nQ[(5, 6)] = 2.0\nQ[(6, 6)] = -4.0\n\nSimulatedAnnealingSampler result:\nSample: {0: np.int8(1), 1: np.int8(0), 2: np.int8(0), 3: np.int8(1), 4: np.int8(1), 5: np.int8(0), 6: np.int8(0)}\nQUBO energy: -10.0\nCut value: 10\n\nBrute-force result:\nBest assignment: {0: 0, 1: 1, 2: 1, 3: 0, 4: 0, 5: 1, 6: 1}\nBest QUBO energy: -10.0\nBest cut value: 10\n\nSA matches brute-force cut: True\nSA matches brute-force energy: True'


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

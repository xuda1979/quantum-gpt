# Auto-generated from distillation reference (row qc-0413).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 4), (0, 5), (1, 2), (1, 5), (1, 6), (2, 5), (2, 6), (3, 5), (4, 6)]\nNodes: [0, 1, 2, 3, 4, 5, 6]\n\nQUBO dictionary:\nQ[(0, 0)] = -2\nQ[(0, 4)] = 2\nQ[(0, 5)] = 2\nQ[(1, 1)] = -3\nQ[(1, 2)] = 2\nQ[(1, 5)] = 2\nQ[(1, 6)] = 2\nQ[(2, 2)] = -3\nQ[(2, 5)] = 2\nQ[(2, 6)] = 2\nQ[(3, 3)] = -1\nQ[(3, 5)] = 2\nQ[(4, 4)] = -2\nQ[(4, 6)] = 2\nQ[(5, 5)] = -4\nQ[(6, 6)] = -3\n\nSimulated Annealing result:\nAssignment: {0: np.int8(0), 1: np.int8(0), 2: np.int8(0), 3: np.int8(0), 4: np.int8(0), 5: np.int8(1), 6: np.int8(1)}\nQUBO energy: 2.0\nCut value: 7\n\nBrute-force verification:\nBest assignment: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1}\nBest cut value: 7\n\nMatch: True'


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

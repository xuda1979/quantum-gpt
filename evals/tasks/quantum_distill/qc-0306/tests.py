# Auto-generated from distillation reference (row qc-0306).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 1), (0, 2), (0, 4), (0, 6), (1, 2), (1, 4), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (3, 4), (3, 6)]\nNumber of nodes: 7\n\nSimulated Annealing result:\nSample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(0), 3: np.int8(1), 4: np.int8(0), 5: np.int8(1), 6: np.int8(0)}\nQUBO energy: -10.0\nMaxCut value: 10\n\nBrute force result:\nSample: {0: 0, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1}\nQUBO energy: -10.0\nMaxCut value: 10\n\nMatch: True'


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

# Auto-generated from distillation reference (row qc-0730).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]\nQUBO dictionary: {(0, 0): -4, (1, 1): -3, (0, 1): 2, (2, 2): -3, (0, 2): 2, (3, 3): -4, (0, 3): 2, (4, 4): -4, (0, 4): 2, (1, 3): 2, (1, 4): 2, (2, 3): 2, (2, 4): 2, (3, 4): 2}\n\nSimulated Annealing result:\nAssignment: {0: np.int8(1), 1: np.int8(0), 2: np.int8(0), 3: np.int8(0), 4: np.int8(1)}\nQUBO energy: -6.0\nMaxCut value: 6\n\nBrute force result:\nAssignment: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1}\nMaxCut value: 6\n\nMatch: True'


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

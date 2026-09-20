# Auto-generated from distillation reference (row qc-0210).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 3), (1, 2), (1, 3), (2, 4), (3, 4)]\nQUBO: {(0, 0): -1, (3, 3): -3, (0, 3): 2, (1, 1): -2, (2, 2): -2, (1, 2): 2, (1, 3): 2, (4, 4): -2, (2, 4): 2, (3, 4): 2}\nSA sample: {0: np.int8(0), 1: np.int8(0), 2: np.int8(1), 3: np.int8(1), 4: np.int8(0)}\nSA energy: -5.0\nSA cut value: 5\nBrute force best sample: {0: 0, 1: 0, 2: 1, 3: 1, 4: 0}\nBrute force best energy: -5\nBrute force best cut value: 5\nSA matches brute force cut: True'


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

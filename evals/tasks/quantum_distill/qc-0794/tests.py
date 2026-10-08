# Auto-generated from distillation reference (row qc-0794).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph edges: [(0, 1), (0, 2), (0, 4), (0, 5), (0, 6), (1, 2), (1, 3), (1, 6), (2, 4), (2, 6), (3, 5), (3, 6), (4, 5), (5, 6)]\nQUBO: {(0, 0): 5, (1, 1): 4, (0, 1): -2, (2, 2): 4, (0, 2): -2, (4, 4): 3, (0, 4): -2, (5, 5): 4, (0, 5): -2, (6, 6): 5, (0, 6): -2, (1, 2): -2, (3, 3): 3, (1, 3): -2, (1, 6): -2, (2, 4): -2, (2, 6): -2, (3, 5): -2, (3, 6): -2, (4, 5): -2, (5, 6): -2}\nSA solution: {0: np.int8(0), 1: np.int8(0), 2: np.int8(0), 3: np.int8(0), 4: np.int8(0), 5: np.int8(0), 6: np.int8(0)}\nSA energy (QUBO): 0.0\nSA MaxCut value: 0\nBrute-force best assignment: {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 1}\nBrute-force MaxCut value: 10\nMatch: False'


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

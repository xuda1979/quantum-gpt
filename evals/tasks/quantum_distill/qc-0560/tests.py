# Auto-generated from distillation reference (row qc-0560).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Random circuit: 5 qubits, depth 8\nBasis gates: ['rz', 'sx', 'x', 'cx']\nCoupling map (line): [[0, 1], [1, 2], [2, 3], [3, 4]]\n--------------------------------------------------\nOptimization level 0: depth = 44, CX count = 16\nOptimization level 1: depth = 43, CX count = 16\nOptimization level 2: depth = 34, CX count = 16\nOptimization level 3: depth = 34, CX count = 16"


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

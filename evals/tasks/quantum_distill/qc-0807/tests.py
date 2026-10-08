# Auto-generated from distillation reference (row qc-0807).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Edges: [(0, 1), (0, 3), (1, 3), (1, 4), (2, 4)]\n\nQUBO (BQM):\nBinaryQuadraticModel({0: 0.0, 1: 0.0, 3: 0.0, 4: 0.0, 2: 0.0}, {(1, 0): -1.0, (3, 0): -1.0, (3, 1): -1.0, (4, 1): -1.0, (2, 4): -1.0}, 0.0, 'BINARY')\n\nSimulated Annealing result:\nBest sample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1)}\nEnergy: -5.0\nCut value: 5.0\n\nBrute force result:\nMax cut value: 4\nOptimal assignments: [(0, 0, 0, 1, 1), (0, 1, 1, 0, 0), (0, 1, 1, 1, 0), (1, 0, 0, 0, 1), (1, 0, 0, 1, 1), (1, 1, 1, 0, 0)]\n\nMatch: False"


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

# Auto-generated from distillation reference (row qc-0398).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Edges: [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3)]\n\nQUBO (BQM):\nBinaryQuadraticModel({0: -4.0, 1: -2.0, 2: -1.0, 3: -2.0, 4: -1.0}, {(1, 0): 2.0, (2, 0): 2.0, (3, 0): 2.0, (3, 1): 2.0, (4, 0): 2.0}, 0.0, 'BINARY')\n\nSimulated Annealing best sample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(0), 3: np.int8(0), 4: np.int8(0)}\nSimulated Annealing energy: -4.0\nSimulated Annealing cut value: 4\n\nBrute force best energy: -4.0\nBrute force best cut value: 4\nNumber of optimal assignments (brute force): 6\nOptimal assignments (brute force):\n{0: 0, 1: 0, 2: 1, 3: 1, 4: 1} cut = 4\n{0: 0, 1: 1, 2: 1, 3: 0, 4: 1} cut = 4\n{0: 0, 1: 1, 2: 1, 3: 1, 4: 1} cut = 4\n{0: 1, 1: 0, 2: 0, 3: 0, 4: 0} cut = 4\n{0: 1, 1: 0, 2: 0, 3: 1, 4: 0} cut = 4\n{0: 1, 1: 1, 2: 0, 3: 0, 4: 0} cut = 4\n\nVerification PASSED: Simulated Annealing matches brute force optimum."


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

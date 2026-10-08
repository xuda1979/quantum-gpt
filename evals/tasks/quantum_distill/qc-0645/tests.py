# Auto-generated from distillation reference (row qc-0645).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Ising chain BQM:\nBinaryQuadraticModel({0: -0.88, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}, {(1, 0): -1.24, (2, 1): -1.24, (3, 2): -1.24, (4, 3): -1.24}, 0.0, 'SPIN')\n\nBest sample from SimulatedAnnealingSampler: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1)}\nBest energy: -5.840000000000001\n\nExpected ground state (all spins aligned with field on spin 0): {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}\nExpected ground state energy: -5.840000000000001\n\nGround state is fully aligned: True\nEnergies match: True\n\nVerification PASSED: ground state is fully aligned."


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

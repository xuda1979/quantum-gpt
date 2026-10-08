# Auto-generated from distillation reference (row qc-0686).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Ising chain parameters:\nN = 5, J = 1.55, h_0 = -0.66, h_i = 0 for i != 0\n\nExact ground-state energy: -6.859999999999999\nExact ground state(s):\n{0: 1, 1: 1, 2: 1, 3: 1, 4: 1}\n\nSimulatedAnnealingSampler best sample:\nenergy: -6.859999999999999\nstate: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1)}\n\nExpected ground state (fully aligned against field on spin 0):\n{0: 1, 1: 1, 2: 1, 3: 1, 4: 1}\n\nBest sample matches an exact ground state: True\nBest sample matches expected fully-aligned state: True\nVERIFIED: Ground state is fully aligned against the field on spin 0.'


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

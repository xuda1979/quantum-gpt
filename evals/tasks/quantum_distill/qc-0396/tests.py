# Auto-generated from distillation reference (row qc-0396).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Ising chain: N=10, J=1.37, h_0=-0.63\nBest sample energy: -12.960000\nBest sample state: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1), 5: np.int8(1), 6: np.int8(1), 7: np.int8(1), 8: np.int8(1), 9: np.int8(1)}\nExpected ground state: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}\nExpected ground state energy: -12.960000\nSpin 0 aligned against field (s_0 = +1): True\nAll spins fully aligned (all +1): True\nVERIFIED: Ground state is fully aligned against the field on spin 0.'


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

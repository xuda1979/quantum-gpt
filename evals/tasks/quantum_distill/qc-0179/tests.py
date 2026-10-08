# Auto-generated from distillation reference (row qc-0179).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Loschmidt Echo Test ===\nNumber of qubits: 3\nNumber of layers: 3\nEcho (U then U^dagger) probability of |000>: 1.0000000000\nReturns to |000> with probability ~1: True\n\n=== Perturbed Loschmidt Echo ===\nPerturbed layer 1, qubit 1\nPerturbation amount: 0.35 radians\nEcho decay (probability of |000>): 0.9697263837\nEcho decay (1 - probability): 0.0302736163'


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

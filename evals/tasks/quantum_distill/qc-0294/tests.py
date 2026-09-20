# Auto-generated from distillation reference (row qc-0294).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Hamiltonian: SparsePauliOp(['ZII', 'IZI', 'IIZ', 'XXI', 'IXX', 'XII'],\ncoeffs=[-1. +0.j, -1. +0.j, -1. +0.j, 0.5+0.j, 0.5+0.j, 0.5+0.j])\nNumber of qubits: 3\nAnsatz: RealAmplitudes, reps = 2\nOptimizer: COBYLA, maxiter = 100\nRandom seed for initial parameters: 42\nInitial parameters: [4.86290927 2.75755456 5.39472984 4.38169255 0.59173373 6.13001603\n4.78238179 4.93898769 0.80496169]\nOptimized parameters: [6.53659971 2.83106948 5.84537625 6.23343272 1.25554293 7.54245567\n6.29142715 4.77674355 0.79044863]\nFinal VQE energy: -3.2508056210623484\nExact ground state energy: -3.253813193819754\nEnergy difference: 0.0030075727574057076"


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

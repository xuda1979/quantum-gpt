# Auto-generated from distillation reference (row qc-0329).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Quantum Fourier Transform circuit (2 qubits):\n┌───┐\nq_0: ┤ H ├─■─────────────X─\n└───┘ │P(π/2) ┌───┐ │\nq_1: ──────■───────┤ H ├─X─\n└───┘\n\nUnitary from Qiskit Operator:\n[[ 0.5+0.j 0.5+0.j 0.5+0.j 0.5+0.j ]\n[ 0.5+0.j 0.5+0.j -0.5+0.j -0.5+0.j ]\n[ 0.5+0.j -0.5+0.j 0. +0.5j -0. -0.5j]\n[ 0.5+0.j -0.5+0.j -0. -0.5j 0. +0.5j]]\n\nExact 4x4 DFT matrix:\n[[ 0.5+0.j 0.5+0.j 0.5+0.j 0.5+0.j ]\n[ 0.5+0.j 0. +0.5j -0.5+0.j -0. -0.5j]\n[ 0.5+0.j -0.5+0.j 0.5-0.j -0.5+0.j ]\n[ 0.5+0.j -0. -0.5j -0.5+0.j 0. +0.5j]]\n\nMax absolute difference between Qiskit and exact DFT:\n0.7071067811865476\n\nMatrices match: False'


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

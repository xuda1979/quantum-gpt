# Auto-generated from distillation reference (row qc-0741).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Quantum Fourier Transform Circuit (3 qubits):\n┌───┐\nq_0: ┤ H ├─■────────■───────────────────────────X─\n└───┘ │P(π/2) │ ┌───┐ │\nq_1: ──────■────────┼───────┤ H ├─■─────────────┼─\n│P(π/4) └───┘ │P(π/2) ┌───┐ │\nq_2: ───────────────■─────────────■───────┤ H ├─X─\n└───┘\n\n==================================================\n\nQiskit Operator Matrix:\n[[ 0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j\n0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j ]\n[ 0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j\n-0.3536+0.j -0.3536+0.j -0.3536+0.j -0.3536+0.j ]\n[ 0.3536+0.j 0.3536+0.j -0.3536+0.j -0.3536+0.j\n0. +0.3536j 0. +0.3536j -0. -0.3536j -0. -0.3536j]\n[ 0.3536+0.j 0.3536+0.j -0.3536+0.j -0.3536+0.j\n-0. -0.3536j -0. -0.3536j 0. +0.3536j 0. +0.3536j]\n[ 0.3536+0.j -0.3536+0.j 0. +0.3536j -0. -0.3536j\n0.25 +0.25j -0.25 -0.25j -0.25 +0.25j 0.25 -0.25j ]\n[ 0.3536+0.j -0.3536+0.j 0. +0.3536j -0. -0.3536j\n-0.25 -0.25j 0.25 +0.25j 0.25 -0.25j -0.25 +0.25j ]\n[ 0.3536+0.j -0.3536+0.j -0. -0.3536j 0. +0.3536j\n-0.25 +0.25j 0.25 -0.25j 0.25 +0.25j -0.25 -0.25j ]\n[ 0.3536+0.j -0.3536+0.j -0. -0.3536j 0. +0.3536j\n0.25 -0.25j -0.25 +0.25j -0.25 -0.25j 0.25 +0.25j ]]\n\nExact DFT Matrix (bit-reversed indexing for Qiskit convention):\n[[ 0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j\n0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j ]\n[ 0.3536+0.j 0.3536-0.j 0.3536-0.j 0.3536-0.j\n-0.3536+0.j -0.3536+0.j -0.3536+0.j -0.3536+0.j ]\n[ 0.3536+0.j 0.3536-0.j -0.3536+0.j -0.3536+0.j\n0. +0.3536j 0. +0.3536j -0. -0.3536j -0. -0.3536j]\n[ 0.3536+0.j 0.3536-0.j -0.3536+0.j -0.3536+0.j\n-0. -0.3536j -0. -0.3536j 0. +0.3536j 0. +0.3536j]\n[ 0.3536+0.j -0.3536+0.j 0. +0.3536j -0. -0.3536j\n0.25 +0.25j -0.25 -0.25j -0.25 +0.25j 0.25 -0.25j ]\n[ 0.3536+0.j -0.3536+0.j 0. +0.3536j -0. -0.3536j\n-0.25 -0.25j 0.25 +0.25j 0.25 -0.25j -0.25 +0.25j ]\n[ 0.3536+0.j -0.3536+0.j -0. -0.3536j 0. +0.3536j\n-0.25 +0.25j 0.25 -0.25j 0.25 +0.25j -0.25 -0.25j ]\n[ 0.3536+0.j -0.3536+0.j -0. -0.3536j 0. +0.3536j\n0.25 -0.25j -0.25 +0.25j -0.25 -0.25j 0.25 +0.25j ]]\n\n==================================================\nFrobenius norm of difference: 4.34e-15\nSUCCESS: The Qiskit QFT circuit exactly matches the DFT matrix.'


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

# Auto-generated from distillation reference (row qc-0482).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Circuit:\n┌───────────┐\nq_0: ┤ Ry(0.889) ├──■──\n└───────────┘┌─┴─┐\nq_1: ─────────────┤ X ├\n└───┘\n\nStatevector: [0.90282578+0.j 0. +0.j 0. +0.j 0.43000652+0.j]\nReduced density matrix (qubit 0):\n[[0.81509439+0.j 0. +0.j]\n[0. +0.j 0.18490561+0.j]]\n\nNumerical entanglement entropy: 0.6906918989268299\nAnalytic entanglement entropy: 0.6906918989268299\nDifference: 0.0'


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

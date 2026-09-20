# Auto-generated from distillation reference (row qc-0386).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Quantum Circuit for the 3-qubit W state:\n┌────────────┐ ┌───┐\nq_0: ┤ Ry(1.9106) ├──■─────────■──┤ X ├\n└────────────┘┌─┴─┐ ┌─┴─┐└───┘\nq_1: ──────────────┤ H ├──■──┤ X ├─────\n└───┘┌─┴─┐└───┘\nq_2: ───────────────────┤ X ├──────────\n└───┘\n\nStatevector amplitudes:\n|000> : 0j\n|001> : (0.5773502691896258+0j)\n|010> : (0.5773502691896257+0j)\n|011> : 0j\n|100> : (0.5773502691896257+0j)\n|101> : 0j\n|110> : 0j\n|111> : 0j\n\nVerification against expected W state amplitudes:\nExpected amplitudes: [0. +0.j 0.57735027+0.j 0.57735027+0.j 0. +0.j\n0.57735027+0.j 0. +0.j 0. +0.j 0. +0.j]\nObtained amplitudes : [0. +0.j 0.57735027+0.j 0.57735027+0.j 0. +0.j\n0.57735027+0.j 0. +0.j 0. +0.j 0. +0.j]\nAll close: True'


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

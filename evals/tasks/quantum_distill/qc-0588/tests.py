# Auto-generated from distillation reference (row qc-0588).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Circuit:\n┌───────────┐\nq_0: ┤ Ry(2.406) ├──■──\n└───────────┘┌─┴─┐\nq_1: ─────────────┤ X ├\n└───┘\nState vector: [0.35956 +0.j 0. +0.j 0. +0.j 0.933122+0.j]\nReduced density matrix eigenvalues: [0.129283 0.870717]\nNumerical entanglement entropy: 0.3850222081\nAnalytic entanglement entropy: 0.3850222081\nAbsolute difference: 1.998e-15'


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

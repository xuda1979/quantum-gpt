# Auto-generated from distillation reference (row qc-0049).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Quantum Circuit:\n┌────────────┐ ┌───┐\nq_0: ┤ Ry(1.9106) ├──■─────────■──┤ X ├\n└────────────┘┌─┴─┐ ┌─┴─┐└───┘\nq_1: ──────────────┤ H ├──■──┤ X ├─────\n└───┘┌─┴─┐└───┘\nq_2: ───────────────────┤ X ├──────────\n└───┘\n\nStatevector amplitudes:\n|000>: amplitude=0.000000+0.000000j, probability=0.000000\n|001>: amplitude=0.577350+0.000000j, probability=0.333333\n|010>: amplitude=0.577350+0.000000j, probability=0.333333\n|011>: amplitude=0.000000+0.000000j, probability=0.000000\n|100>: amplitude=0.577350+0.000000j, probability=0.333333\n|101>: amplitude=0.000000+0.000000j, probability=0.000000\n|110>: amplitude=0.000000+0.000000j, probability=0.000000\n|111>: amplitude=0.000000+0.000000j, probability=0.000000\n\nFidelity with ideal W state: 1.0000000000'


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

# Auto-generated from distillation reference (row qc-0352).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Superdense coding to transmit the 2-bit message '11'\nCircuit:\n┌───┐ ┌───┐┌───┐ ┌───┐┌─┐\nq_0: ┤ H ├──■──┤ Z ├┤ X ├──■──┤ H ├┤M├\n└───┘┌─┴─┐└───┘└───┘┌─┴─┐└┬─┬┘└╥┘\nq_1: ─────┤ X ├──────────┤ X ├─┤M├──╫─\n└───┘ └───┘ └╥┘ ║\nc: 2/═══════════════════════════╩═══╩═\n1 0\n\nMeasurement results (1000 shots): {'11': 1000}\nDecoded message '11' verified: True"


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

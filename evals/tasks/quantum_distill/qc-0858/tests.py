# Auto-generated from distillation reference (row qc-0858).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Quantum Circuit:\n┌───┐ ░ ░ ┌───┐┌─┐\nq_0: ┤ H ├──────░───────░─┤ H ├┤M├──────\n├───┤ ░ ░ ├───┤└╥┘┌─┐\nq_1: ┤ H ├──────░───────░─┤ H ├─╫─┤M├───\n├───┤ ░ ░ ├───┤ ║ └╥┘┌─┐\nq_2: ┤ H ├──────░───────░─┤ H ├─╫──╫─┤M├\n├───┤┌───┐ ░ ┌───┐ ░ └───┘ ║ ║ └╥┘\nq_3: ┤ X ├┤ H ├─░─┤ X ├─░───────╫──╫──╫─\n└───┘└───┘ ░ └───┘ ░ ║ ║ ║\nc: 3/═══════════════════════════╩══╩══╩═\n0 1 2\n\nMeasurement outcome: {'000': 1024}\nConclusion: The function is CONSTANT."


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

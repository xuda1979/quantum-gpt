# Auto-generated from distillation reference (row qc-0871).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Bernstein-Vazirani Algorithm\nHidden string s: 0111110\nNumber of qubits: 8\nOracle queries used: 1\n\nQuantum Circuit:\n┌───┐ ░ ░ ┌───┐┌─┐\nq_0: ┤ H ├──────░───────────────────────────░─┤ H ├┤M├──────────────────\n├───┤ ░ ░ ├───┤└╥┘┌─┐\nq_1: ┤ H ├──────░───■───────────────────────░─┤ H ├─╫─┤M├───────────────\n├───┤ ░ │ ░ ├───┤ ║ └╥┘┌─┐\nq_2: ┤ H ├──────░───┼────■──────────────────░─┤ H ├─╫──╫─┤M├────────────\n├───┤ ░ │ │ ░ ├───┤ ║ ║ └╥┘┌─┐\nq_3: ┤ H ├──────░───┼────┼────■─────────────░─┤ H ├─╫──╫──╫─┤M├─────────\n├───┤ ░ │ │ │ ░ ├───┤ ║ ║ ║ └╥┘┌─┐\nq_4: ┤ H ├──────░───┼────┼────┼────■────────░─┤ H ├─╫──╫──╫──╫─┤M├──────\n├───┤ ░ │ │ │ │ ░ ├───┤ ║ ║ ║ ║ └╥┘┌─┐\nq_5: ┤ H ├──────░───┼────┼────┼────┼────■───░─┤ H ├─╫──╫──╫──╫──╫─┤M├───\n├───┤ ░ │ │ │ │ │ ░ ├───┤ ║ ║ ║ ║ ║ └╥┘┌─┐\nq_6: ┤ H ├──────░───┼────┼────┼────┼────┼───░─┤ H ├─╫──╫──╫──╫──╫──╫─┤M├\n├───┤┌───┐ ░ ┌─┴─┐┌─┴─┐┌─┴─┐┌─┴─┐┌─┴─┐ ░ └───┘ ║ ║ ║ ║ ║ ║ └╥┘\nq_7: ┤ X ├┤ H ├─░─┤ X ├┤ X ├┤ X ├┤ X ├┤ X ├─░───────╫──╫──╫──╫──╫──╫──╫─\n└───┘└───┘ ░ └───┘└───┘└───┘└───┘└───┘ ░ ║ ║ ║ ║ ║ ║ ║\nc: 7/═══════════════════════════════════════════════╩══╩══╩══╩══╩══╩══╩═\n0 1 2 3 4 5 6\n\nMeasurement results: {'0111110': 1024}\nRecovered string: 0111110\nMatch: True\n\nThis demonstrates that a single oracle query suffices\nto recover the hidden string, achieving an exponential\nspeedup over the classical O(n) queries required.\n\nHistogram saved to bv_histogram.png"


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

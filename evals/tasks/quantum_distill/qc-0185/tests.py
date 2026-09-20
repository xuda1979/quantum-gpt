# Auto-generated from distillation reference (row qc-0185).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph state stabilizer verification\nCircuit:\n┌───┐\nq_0: ┤ H ├─■──■─────────────────────────\n├───┤ │ │\nq_1: ┤ H ├─■──┼──■──■──■──■─────────────\n├───┤ │ │ │ │ │\nq_2: ┤ H ├────┼──■──┼──┼──┼─────■───────\n├───┤ │ │ │ │ │\nq_3: ┤ H ├────■─────■──┼──┼──■──┼──■────\n├───┤ │ │ │ │ │\nq_4: ┤ H ├─────────────■──┼──■──┼──┼──■─\n├───┤ │ │ │ │\nq_5: ┤ H ├────────────────■─────■──■──■─\n└───┘\n\nK_0 = IIZIZX: expectation = 0.9999999999999996\nK_1 = ZZZZXZ: expectation = 0.9999999999999996\nK_2 = ZIIXZI: expectation = 0.9999999999999996\nK_3 = ZZXIZZ: expectation = 0.9999999999999996\nK_4 = ZXZIZI: expectation = 0.9999999999999996\nK_5 = XZZZZI: expectation = 0.9999999999999996\n\nAll stabilizers have expectation +1: True'


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

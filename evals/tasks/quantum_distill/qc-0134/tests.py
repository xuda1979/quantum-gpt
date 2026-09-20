# Auto-generated from distillation reference (row qc-0134).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph state circuit:\n┌───┐\nq_0: ┤ H ├─■──■───────\n├───┤ │ │\nq_1: ┤ H ├─■──┼──■────\n├───┤ │ │\nq_2: ┤ H ├────■──■──■─\n├───┤ │\nq_3: ┤ H ├──────────■─\n└───┘\n\nStabilizer expectation values:\nK_0 = IZZX: 1.0000000000\nK_1 = IZXZ: 1.0000000000\nK_2 = ZXZZ: 1.0000000000\nK_3 = XZII: 1.0000000000\n\nAll stabilizers have expectation +1: True'


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

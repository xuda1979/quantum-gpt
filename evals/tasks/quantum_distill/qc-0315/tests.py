# Auto-generated from distillation reference (row qc-0315).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'K_0 = ZZZZIX: expectation = 1.000000000000, +1 = True\nK_1 = ZIIZXI: expectation = 1.000000000000, +1 = True\nK_2 = IIZXZZ: expectation = 1.000000000000, +1 = True\nK_3 = IZXZIZ: expectation = 1.000000000000, +1 = True\nK_4 = ZXZIIZ: expectation = 1.000000000000, +1 = True\nK_5 = XZIIZZ: expectation = 1.000000000000, +1 = True\nAll stabilizers have expectation +1: True'


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

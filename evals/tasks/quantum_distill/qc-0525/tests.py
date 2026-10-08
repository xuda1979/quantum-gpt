# Auto-generated from distillation reference (row qc-0525).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'n=1: max abs elementwise difference = 8.660e-17\n\nn=2: max abs elementwise difference = 7.071e-01\n\nn=3: max abs elementwise difference = 7.071e-01\nn=3: max phase difference for |1> input = 3.927e+00\nphases (mod 2pi): [0. 0. 3.14159265 3.14159265 0. 0.\n3.14159265 3.14159265]\nexpected phases : [0. 0.78539816 1.57079633 2.35619449 3.14159265 3.92699082\n4.71238898 5.49778714]\n\nn=4: max abs elementwise difference = 5.000e-01'


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

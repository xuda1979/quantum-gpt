# Auto-generated from distillation reference (row qc-0313).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Kernel matrix K:\n[[1.00000000e+00 3.76684271e-02 3.82071828e-01 2.76757831e-01\n2.99912058e-01]\n[3.76684271e-02 1.00000000e+00 1.79405057e-03 1.20153135e-01\n7.44825403e-01]\n[3.82071828e-01 1.79405057e-03 1.00000000e+00 3.41704839e-01\n7.81486521e-04]\n[2.76757831e-01 1.20153135e-01 3.41704839e-01 1.00000000e+00\n1.40397881e-02]\n[2.99912058e-01 7.44825403e-01 7.81486521e-04 1.40397881e-02\n1.00000000e+00]]\n\nIs symmetric: True\nUnit diagonal: True'


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

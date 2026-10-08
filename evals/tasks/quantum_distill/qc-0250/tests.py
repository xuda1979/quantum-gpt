# Auto-generated from distillation reference (row qc-0250).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Kernel matrix K:\n[[1.00000000e+00 1.29521334e-03 2.48733834e-01 1.09262779e-01\n4.52002028e-05 1.64470440e-04]\n[1.29521334e-03 1.00000000e+00 9.26969272e-09 7.08535741e-02\n1.09382505e-01 3.80730104e-04]\n[2.48733834e-01 9.26969272e-09 1.00000000e+00 9.03100687e-02\n5.81149440e-05 8.26205263e-05]\n[1.09262779e-01 7.08535741e-02 9.03100687e-02 1.00000000e+00\n8.08490091e-02 8.96185147e-03]\n[4.52002028e-05 1.09382505e-01 5.81149440e-05 8.08490091e-02\n1.00000000e+00 7.85838384e-01]\n[1.64470440e-04 3.80730104e-04 8.26205263e-05 8.96185147e-03\n7.85838384e-01 1.00000000e+00]]\n\nMax |K - K^T|: 1.1102230246251565e-16\nMax |diag(K) - 1|: 4.440892098500626e-16\nK is symmetric: True\nK has unit diagonal: True\nVerification PASSED: K is symmetric with unit diagonal.'


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

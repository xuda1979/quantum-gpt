# Auto-generated from distillation reference (row qc-0100).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'phi n=4 n=8 n=12\n------------------------------------------------------------------------\n0.1 2.50e-02 1.56e-03 9.77e-05\n0.25 0.00e+00 0.00e+00 0.00e+00\n0.333333 2.08e-02 1.30e-03 8.10e-05\n0.9 2.50e-02 1.56e-03 9.77e-05\n\nExplanation:\n--------------------------------------------------------------------------------\n\nThe error decreases as n increases because an n-qubit phase register can\nrepresent 2^n discrete phase values uniformly spaced in [0, 1) with spacing\n1/2^n. When we encode phi, it is rounded to the nearest representable value\nk/2^n, introducing a quantization error of at most 1/2^(n+1). As n increases,\nthe spacing 1/2^n shrinks exponentially, so the maximum possible rounding\nerror decreases exponentially. For example, with n=4 the spacing is 1/16=0.0625,\nwith n=8 it is 1/256~0.0039, and with n=12 it is 1/4096~0.000244.\n\nFor phi=0.25, the error is zero for n>=4 because 0.25 is exactly representable\nas k/2^n for any n>=2. Specifically, 0.25 = 1/4 = 2^(n-2)/2^n, so k=2^(n-2)\nis always an integer for n>=2. Since phi maps exactly to a representable\nphase value, the round-trip encoding and decoding introduces no quantization\nerror, resulting in an absolute error of exactly zero.'


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

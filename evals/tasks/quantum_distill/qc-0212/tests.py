# Auto-generated from distillation reference (row qc-0212).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Unitary from circuit:\n[[ 5.000000e-01+0.j 5.000000e-01+0.j 5.000000e-01+0.j\n5.000000e-01+0.j ]\n[ 5.000000e-01+0.j 5.000000e-01+0.j -5.000000e-01+0.j\n-5.000000e-01+0.j ]\n[ 5.000000e-01+0.j -5.000000e-01+0.j 3.061617e-17+0.5j\n-3.061617e-17-0.5j]\n[ 5.000000e-01+0.j -5.000000e-01+0.j -3.061617e-17-0.5j\n3.061617e-17+0.5j]]\n\nDFT matrix:\n[[ 5.00000000e-01+0.0000000e+00j 5.00000000e-01+0.0000000e+00j\n5.00000000e-01+0.0000000e+00j 5.00000000e-01+0.0000000e+00j]\n[ 5.00000000e-01+0.0000000e+00j 3.06161700e-17+5.0000000e-01j\n-5.00000000e-01+6.1232340e-17j -9.18485099e-17-5.0000000e-01j]\n[ 5.00000000e-01+0.0000000e+00j -5.00000000e-01+6.1232340e-17j\n5.00000000e-01-1.2246468e-16j -5.00000000e-01+1.8369702e-16j]\n[ 5.00000000e-01+0.0000000e+00j -9.18485099e-17-5.0000000e-01j\n-5.00000000e-01+1.8369702e-16j 2.75545530e-16+5.0000000e-01j]]\n\nFrobenius norm difference: 1.732050807568877\nMatches DFT up to numerical precision: False'


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

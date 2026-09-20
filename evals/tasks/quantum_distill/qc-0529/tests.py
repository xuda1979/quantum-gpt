# Auto-generated from distillation reference (row qc-0529).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Prepared state: RY(0.633) RZ(4.666)|0>\n<X> = 0.5915661856816615\n<Y> = 5.551115123125783e-17\n<Z> = 0.8062564405684152\nReconstructed density matrix rho:\n[[0.90312822+0.00000000e+00j 0.29578309-2.77555756e-17j]\n[0.29578309+2.77555756e-17j 0.09687178+0.00000000e+00j]]\nFidelity with true state: 1.0000000000000002'


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

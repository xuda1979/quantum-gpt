# Auto-generated from distillation reference (row qc-0353).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Prepared state: RY(2.784) RZ(5.537)|0>\n<X> = 0.350020\n<Y> = -0.000000\n<Z> = -0.936742\n\nReconstructed density matrix:\n[[0.03162892+0.0000000e+00j 0.17501009+6.9388939e-18j]\n[0.17501009-6.9388939e-18j 0.96837108+0.0000000e+00j]]\n\nFidelity with true state: 1.00000000'


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

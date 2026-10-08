# Auto-generated from distillation reference (row qc-0613).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Prepared state: RY(1.396) RZ(5.476)|0>\nTrue statevector: [-0.70457522-0.30087795j -0.5910507 -0.25239906j]\nTrue density matrix:\n[[0.58695379-6.36173713e-18j 0.49238099+4.92929760e-18j]\n[0.49238099+1.73207885e-18j 0.41304621-6.10741007e-18j]]\n\n<X> = 0.984761979642512\n<Y> = 0.0\n<Z> = 0.1739075715734093\n\nReconstructed density matrix:\n[[0.58695379+0.j 0.49238099+0.j]\n[0.49238099+0.j 0.41304621+0.j]]\n\nFidelity with true state: 0.9999999999999996'


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

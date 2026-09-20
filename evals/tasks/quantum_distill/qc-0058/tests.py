# Auto-generated from distillation reference (row qc-0058).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '==================================================\nVQE for 5-site Transverse-Field Ising Model\nParameters: J = 0.65, h = 0.61, Open Boundary\n==================================================\nAnsatz: TwoLocal (reps=2, ry/rz + cx linear)\nNumber of parameters: 30\nOptimizer: COBYLA (maxiter=2000)\n--------------------------------------------------\nVQE Energy: -3.60052610\nExact Energy: -3.76255310\nAbs Error: 0.16202700\nConverged in: 2000 evaluations\n=================================================='


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

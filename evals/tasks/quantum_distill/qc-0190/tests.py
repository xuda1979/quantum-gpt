# Auto-generated from distillation reference (row qc-0190).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== VQE Results (qulacs) ===\nOptimal parameters: [ 2.92070572e+00 7.06804948e+00 6.44073473e+00 3.75560005e+00\n4.22045635e-01 2.57012027e+00 4.46385281e-01 5.50653522e+00\n3.14159296e+00 6.34936774e+00 -2.72735899e-03]\nVQE ground state energy: -1.2101041667\nExact ground state energy: -1.3718600512\nAbsolute error: 1.62e-01\nOptimizer converged: True\nOptimizer message: Return from COBYLA because the trust region radius reaches its lower bound.'


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

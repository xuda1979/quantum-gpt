# Auto-generated from distillation reference (row qc-0130).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Final tableau (columns: sign | x0 x1 | z0 z1):\nrow 0 (destabilizer 0): [0, 0, 0, 1, 0]\nrow 1 (destabilizer 1): [0, 0, 1, 0, 0]\nrow 2 (stabilizer 0): [0, 1, 1, 0, 0]\nrow 3 (stabilizer 1): [0, 0, 0, 1, 1]\n\nVerification of Bell state stabilizers:\nstabilizer 0: sign=0, operator=X⊗X\nstabilizer 1: sign=0, operator=Z⊗Z\n\nAll checks passed: Bell state stabilizers are X⊗X and Z⊗Z with sign bits 0.'


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

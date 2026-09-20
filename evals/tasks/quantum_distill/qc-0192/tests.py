# Auto-generated from distillation reference (row qc-0192).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Statevector: [0.707107+0.j 0. +0.j 0. +0.j 0.707107+0.j]\nProbability |00>: 0.4999999999999999\nProbability |11>: 0.4999999999999999\nOperator matrix U:\n[[ 0.707107+0.j 0.707107+0.j 0. +0.j 0. +0.j]\n[ 0. +0.j 0. +0.j 0.707107+0.j -0.707107+0.j]\n[ 0. +0.j 0. +0.j 0.707107+0.j 0.707107+0.j]\n[ 0.707107+0.j -0.707107+0.j 0. +0.j 0. +0.j]]\nU^dagger U:\n[[ 1.+0.j -0.+0.j 0.+0.j 0.+0.j]\n[-0.+0.j 1.+0.j 0.+0.j 0.+0.j]\n[ 0.+0.j 0.+0.j 1.+0.j 0.+0.j]\n[ 0.+0.j 0.+0.j 0.+0.j 1.+0.j]]\nAll verifications passed: Bell state prepared, probabilities are 0.5 each, and U is unitary.'


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
